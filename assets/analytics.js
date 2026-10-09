// Public Cloudflare site token, not an account credential. Respect browser opt-outs.
if (['nychousingdata.com', 'www.nychousingdata.com'].includes(location.hostname)
    && navigator.doNotTrack !== '1' && !navigator.globalPrivacyControl) {
  const beacon = document.createElement('script');
  beacon.type = 'module';
  beacon.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  beacon.dataset.cfBeacon = JSON.stringify({token:'d1216bcae9cb43de89f821d3bb3bf65f'});
  document.body.append(beacon);
}
