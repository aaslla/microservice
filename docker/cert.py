import datetime
import os
import logging
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
logger = logging.getLogger('Certification-Service')


def create_private_key(path: str):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    logger.info("Creating new private key in " + path)
    with open(path, "wb") as key_file:
        key_file.write(key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    return key


def get_private_key():
    if os.path.isfile('./privateKey.pem'):
        with open("privateKey.pem", "rb") as key_file:
            key = load_pem_private_key(
                data=key_file.read(), password=None)
        logger.info("Using private key from existing file")
        return key
    logger.debug("Could not read existing private key")
    return create_private_key('privateKey.pem')


def get_CA_certificate():
    if os.path.isfile("./caCert.pem"):
        with open("./caCert.pem", "rb") as cert_file:
            cert = x509.load_pem_x509_certificate(cert_file.read())

        logger.info("Using certificate from existing file")
        return cert
    logger.debug("Could not read existing certificate")
    key = get_private_key()
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, u"ca_cert")])
    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(datetime.datetime.utcnow()).not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365)).add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=False).sign(
        key, hashes.SHA256())
    logger.debug("Creating new self signed certificate")
    with open("./caCert.pem", "wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.DER))
    return cert


def create_certificate_signing_requests(device_id: str):
    logging.info("Create certificate signing request for device " + device_id)
    key = create_private_key(device_id+"_privateKey.pem")
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, device_id)])).add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=False).sign(key, hashes.SHA256())  # Maybe add more info here
    return csr


def create_certificate_for_device(device_id: str, valid: int):
    logging.info("Create certificate for device " + device_id)
    ca_cert = get_CA_certificate()
    private_ca_key = get_private_key()
    csr = create_certificate_signing_requests(device_id)
    cert = x509.CertificateBuilder().subject_name(csr.subject).issuer_name(ca_cert.subject).public_key(csr.public_key()).serial_number(x509.random_serial_number()
                                                                                                                                       ).not_valid_before(datetime.datetime.utcnow()).not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=valid)).add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=False).sign(private_ca_key, hashes.SHA256())

    with open(device_id+".pem", "wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.DER))

    return cert.public_bytes(serialization.Encoding.DER)
