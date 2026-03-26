import datetime
import socket
import ssl

from dependencies.modules.base import BaseModule


class Module(BaseModule):
    name = "TLS Certificate"
    description = "Check for TLS certificate misconfigurations and expiry"
    severity = "medium"

    EXPIRY_WARNING_DAYS = 30

    def _get_certificate(self) -> dict | None:
        """Fetch the TLS certificate from the target."""
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(
                socket.create_connection(
                    (self.target.hostname, self.target.port), timeout=5
                ),
                server_hostname=self.target.hostname,
            ) as ssock:
                return ssock.getpeercert()
        except ssl.SSLError:
            # Re-fetch without verification to still inspect the cert
            try:
                ctx = ssl._create_unverified_context()
                with ctx.wrap_socket(
                    socket.create_connection(
                        (self.target.hostname, self.target.port), timeout=5
                    ),
                    server_hostname=self.target.hostname,
                ) as ssock:
                    return ssock.getpeercert()
            except Exception:
                return None
        except Exception:
            return None

    def _check_expiry(self, cert: dict) -> None:
        """Check if the certificate is expired or expiring soon."""
        expiry_str = cert.get("notAfter")
        if not expiry_str:
            return
        expiry = datetime.datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
        now = datetime.datetime.utcnow()
        delta = expiry - now

        if delta.days < 0:
            self.findings.append(
                f"Certificate expired {abs(delta.days)} days ago (expired {expiry.strftime('%Y-%m-%d')})"
            )
        elif delta.days < self.EXPIRY_WARNING_DAYS:
            self.findings.append(
                f"Certificate expires in {delta.days} days ({expiry.strftime('%Y-%m-%d')})"
            )

    def _check_hostname(self, cert: dict) -> None:
        """Check if the certificate hostname matches the target."""
        san = cert.get("subjectAltName", [])
        valid_names = [name for _, name in san if _ == "DNS"]
        # Fall back to commonName if no SAN
        if not valid_names:
            subject = dict(x[0] for x in cert.get("subject", []))
            cn = subject.get("commonName")
            if cn:
                valid_names.append(cn)
        match = any(
            self.target.hostname == name
            or (name.startswith("*.") and self.target.hostname.endswith(name[1:]))
            for name in valid_names
        )
        if not match:
            self.findings.append(
                f"Certificate hostname mismatch — cert valid for {valid_names}, got {self.target.hostname}"
            )

    def _check_weak_signature(self) -> None:
        """Check if the certificate uses a weak signature algorithm (MD5 / SHA1)."""
        try:
            ctx = ssl._create_unverified_context()
            with ctx.wrap_socket(
                socket.create_connection(
                    (self.target.hostname, self.target.port), timeout=5
                ),
                server_hostname=self.target.hostname,
            ) as ssock:
                der = ssock.getpeercert(binary_form=True)
                if der is None:
                    return
                pem = ssl.DER_cert_to_PEM_cert(der)
                # Weak algorithms leave traces in the PEM metadata header
                cipher = ssock.cipher()
                if cipher and ("MD5" in cipher[0] or "SHA1" in cipher[0]):
                    self.findings.append(f"Weak cipher in use: {cipher[0]}")
                if "sha1" in pem.lower() and "sha1withrsaencryption" in pem.lower():
                    self.findings.append(
                        "Certificate uses weak SHA-1 signature algorithm"
                    )
        except Exception:
            pass

    def _check_self_signed(self, cert: dict) -> None:
        """Check if the certificate is self-signed."""
        subject = dict(x[0] for x in cert.get("subject", []))
        issuer = dict(x[0] for x in cert.get("issuer", []))
        if subject == issuer:
            self.findings.append(
                f"Certificate is self-signed (issuer == subject: {subject.get('commonName', 'unknown')})"
            )

    def _check_not_yet_valid(self, cert: dict) -> None:
        """Check if the certificate is not yet valid."""
        start_str = cert.get("notBefore")
        if not start_str:
            return
        start = datetime.datetime.strptime(start_str, "%b %d %H:%M:%S %Y %Z")
        if datetime.datetime.utcnow() < start:
            self.findings.append(
                f"Certificate is not yet valid (valid from {start.strftime('%Y-%m-%d')})"
            )

    def _run(self) -> bool:
        # Only applicable to HTTPS targets
        if not self.target.url.startswith("https://"):
            return False

        cert = self._get_certificate()
        if cert is None:
            self.findings.append("Could not retrieve TLS certificate")
            return True

        self._check_expiry(cert)
        self._check_not_yet_valid(cert)
        self._check_hostname(cert)
        self._check_self_signed(cert)
        self._check_weak_signature()

        return len(self.findings) > 0
