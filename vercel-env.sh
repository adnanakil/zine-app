#!/bin/bash

# Clean script to set Firebase environment variables in Vercel
echo "Setting Firebase environment variables..."

# Set each variable using echo with -n to avoid newlines
echo -n "archgest-20638" | vercel env add FIREBASE_PROJECT_ID production
echo -n "archgest-20638.firebasestorage.app" | vercel env add FIREBASE_STORAGE_BUCKET production
echo -n "1039573653180" | vercel env add FIREBASE_MESSAGING_SENDER_ID production
echo -n "1:1039573653180:web:2d519f98f4203a015362b9" | vercel env add FIREBASE_APP_ID production
echo -n "G-9YR88606QT" | vercel env add FIREBASE_MEASUREMENT_ID production

echo "Done setting Firebase environment variables!"