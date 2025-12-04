# Progressive Web App (PWA) Setup for FinCo

FinCo is now a Progressive Web App! This means users can install it on their devices and use it like a native app.

## What is a PWA?

A Progressive Web App allows users to:

- **Install** the app on their device (mobile or desktop)
- **Run offline** with cached content
- **Access quickly** from their home screen or app drawer
- **Experience** a native app-like interface without browser UI

## How Users Can Install

### On Desktop (Chrome/Edge)

1. Visit the FinCo app URL
2. Look for the install icon (⊕) in the address bar
3. Click it and select "Install"
4. The app will open in its own window

### On Mobile (Android)

1. Open the app in Chrome
2. Tap the menu (⋮) → "Add to Home screen" or "Install app"
3. Confirm installation
4. The app icon will appear on your home screen

### On iOS (Safari)

1. Open the app in Safari
2. Tap the Share button (□↑)
3. Scroll down and tap "Add to Home Screen"
4. Name it and tap "Add"
5. The app icon will appear on your home screen

## Technical Details

### Files Created

- **`static/manifest.json`** - Web app manifest defining app metadata, icons, and display settings
- **`static/sw.js`** - Service worker providing offline caching and performance optimization
- **`static/icons/`** - PWA icons in multiple sizes:
  - `icon-192.png` - 192×192 for Android
  - `icon-512.png` - 512×512 for Android splash screen
  - `apple-touch-icon.png` - 180×180 for iOS devices

### Integration

PWA support is integrated into `app.py` with:

- Meta tags for mobile web app capabilities
- Service worker registration
- Manifest linking
- Theme color configuration

### Requirements

- **HTTPS**: PWA features require HTTPS (automatically available on Streamlit Cloud)
- **Browser Support**: Works on Chrome, Edge, Safari (iOS 11.3+), and other modern browsers

## Hosting Considerations

When deploying to **Streamlit Cloud**:

1. The `static/` folder will be automatically served at `/app/static/`
2. PWA features work out of the box with HTTPS
3. Users will see the install prompt when visiting the app

## Offline Functionality

The service worker implements a **network-first** caching strategy:

- Tries to fetch from network first for fresh content
- Falls back to cache if network is unavailable
- Caches successful responses for future offline access
- Provides basic offline functionality for viewed pages

## Customization

To customize the PWA:

- **App name**: Edit `name` and `short_name` in `static/manifest.json`
- **Colors**: Update `theme_color` and `background_color` in manifest
- **Icons**: Replace files in `static/icons/` (maintain sizes)
- **Caching strategy**: Modify `static/sw.js` cache behavior

## Testing

Test the PWA locally:

```bash
# Run with HTTPS (required for service workers)
streamlit run app.py --server.enableCORS=false
```

For full PWA testing, deploy to Streamlit Cloud or another HTTPS-enabled hosting service.
