#!/bin/bash

# Set all environment variables for Vercel production

echo "Setting environment variables for Vercel..."

# Basic config
echo "zine-app-production-secret-key-2024-change-this" | vercel env add SECRET_KEY production
echo "sqlite:///zines.db" | vercel env add DATABASE_URL production

# Firebase Frontend Config
echo "AIzaSyBSYJd9hGVT8YoUmgJXoLQMhILSQe6t4QE" | vercel env add FIREBASE_API_KEY production
echo "archgest-20638.firebaseapp.com" | vercel env add FIREBASE_AUTH_DOMAIN production
echo "archgest-20638" | vercel env add FIREBASE_PROJECT_ID production
echo "archgest-20638.firebasestorage.app" | vercel env add FIREBASE_STORAGE_BUCKET production
echo "1039573653180" | vercel env add FIREBASE_MESSAGING_SENDER_ID production
echo "1:1039573653180:web:2d519f98f4203a015362b9" | vercel env add FIREBASE_APP_ID production
echo "G-9YR88606QT" | vercel env add FIREBASE_MEASUREMENT_ID production

# Firebase Admin SDK Config
echo "8ae833316034a7746167d59a007a5a40345aed0a" | vercel env add FIREBASE_PRIVATE_KEY_ID production
echo "-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC9/lou/voJjIUT
UWfge+Ou3qfeTnxKIf6FiOyvpfjUN6qKsFXa2GvWSEbPuoGGYqTX3Frx39BWjqFE
4qK0f7sjIrGCkoDdN8km4YKBtvj3ZfFYJPQVsmKEVEoyeNRaCa4v1AEaoLVRGvRC
xNG/tdxDXXVj8pBXoGVIfIGNAoO/6cZfmBEge+H9ub8Y0348jFlR5iVOjSmN659c
tmrx50PEKVWusGXMD8lMb/UuVauyVXsZ0lMMmC3Crktj9Zehvx3Ud4UekdVgL+Te
pR8Lg+5PHc8Wn+1nFMMriKgyIV+JfsP1Ax6IydoAWgyJmCrBfpD4ZsluxIiC8lX+
1/mzLApVAgMBAAECggEAA7qnUyl8B43zhWKL/b2mGruSDeylHIti7y9gfejDDony
gKW0ubE/xJqckTKMR51OC6fukmAd5bpc804uJV7QcdXE0tbvTT2YEXmhpyF2l4cv
tSwx15nYZy0vBk3q1RhANqjG8MUwvzZz5DpFZ6mOeOAFECt6+81RJPAUrDYywc8w
fwi7d74TC7WonAfwk9Yl2SJI9QbDBVTgnuix+zCrB+Lpl34XHT8MQLQoRUGBZ4oJ
fv66MD1mdpYA25q0jB0Ci/J1lgbJuwn0ndKHaHloIKNmrbwQ/X4MFLgxJhyElESl
WDTxtMG2QzXITRhE+Xd8tZJyia5I5Ln21w8Q1uZKzQKBgQDvFj/5LHSYRSlVnaXM
Pvy0cyAeneTQ4+LKAIPM/sUdj2PftT/nqISU9WA3VC/rOuZTSMxNyeiDyJSUe8vL
ZKnd4yWU6KdDIbXgC5wFegTKNMMtcowrHuHPuzwoPhbRERESLPIbXpodaWAw2rfW
o+YuLYPD+rcWvjIGnnwK15oLwwKBgQDLbwuSYsWnsvvzD/+7/Fr3vLcl8JjySRFm
jRe0mA3fPxCo6HQnPB+BE6V4+hnP6hyfngf5ZHfMvbS5tHCd+HHLEBmTxVT1yUC0
ZmkcIK4S589bA/fM9016exVtRyaalZlbzfGIYYuOTirHHeW03tXwXOKVOAIa6vRWT
K3CVo6/oBwKBgE3JBWNCDWUFC1+pfKmozHrBAfA0Gp/DpKNn63mkYekuH6ZGx9XM
w+Xat0UJBNYZQZpTEvUz/YvylDSC2lkAFSv1nOKHlvOGYi/UVxyJCEnpRJ7ip6vX
zkvRdM769F1smgs5yEMTUjzDbeI3JpyUkmzvrfDy/uJNWuVAZsb4QkwVAoGBAIYp
nNMUys+3LYv2MCz017VsQskFrIiVAaHFSS3z3aoueDk83GWHtCs3HrjzEBTbi7cE
zLN/u7ZOIiMaye6Ui89ktcmLqWVTLZYLuCSP6JOOKUIr+L/8ZvmEpJ4CxCFupcd8
b2EvznBeVrJ79Th5OvZBiFsx46jBzLm7O0ukoPz/AoGBAL96Ss35pBeq1AVVzXWY
Iwx3zPo28qVekzmU9WSE1eZRG1CymS4zdDvFPHfdIlkSjND+3eP9Azb6yPTqJ4BX
43su8tYbKgrsR8hJfrvYznuuxpbmIleVrDv2pBC2tikin0lI8zHLcZg017OOMBIP
Nnnvm3vWLKiP9pUdcoOCMbXb
-----END PRIVATE KEY-----" | vercel env add FIREBASE_PRIVATE_KEY production
echo "firebase-adminsdk-fbsvc@archgest-20638.iam.gserviceaccount.com" | vercel env add FIREBASE_CLIENT_EMAIL production
echo "103978167173051622695" | vercel env add FIREBASE_CLIENT_ID production
echo "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40archgest-20638.iam.gserviceaccount.com" | vercel env add FIREBASE_CLIENT_CERT_URL production

echo "All environment variables set! Now deploying to production..."
vercel --prod