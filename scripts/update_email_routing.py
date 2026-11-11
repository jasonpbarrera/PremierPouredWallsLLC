#!/usr/bin/env python3
"""
Updates Cloudflare Email Routing rules for premierpouredwalls.com
to forward info@ and scott@ directly to premierpouredwalls@gmail.com
once verified in Cloudflare.
"""
import urllib.request
import json
import sys

def main():
    # 1. Fetch Cloudflare credentials from portal settings
    portal_req = urllib.request.Request(
        'https://purple-flower-020acac0f.4.azurestaticapps.net/api/portal-settings',
        headers={'x-admin-passcode': 'JBDigital2026!'}
    )
    settings = json.loads(urllib.request.urlopen(portal_req).read().decode('utf-8'))
    token = settings['cloudflareApiToken']
    zone_id = '23a252d1c1ce5b4e02e9c373ec1f4fe3'
    account_id = 'ec917b2b52a2809f5b1b478ee838f5cb'
    dest_id = '0917e4bd98af4e85aff3e4644aa96edd'
    target_email = 'premierpouredwalls@gmail.com'

    # 2. Check destination status
    dest_req = urllib.request.Request(
        f'https://api.cloudflare.com/client/v4/accounts/{account_id}/email/routing/addresses/{dest_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    dest_res = json.loads(urllib.request.urlopen(dest_req).read().decode('utf-8'))['result']
    print(f"Destination: {dest_res['email']} | Status: {dest_res['status']}")

    if dest_res['status'] != 'verified':
        print(f"\n⚠️  {target_email} is still unverified.")
        print(f"Please click the verification link in the confirmation email Cloudflare sent to {target_email}.")
        sys.exit(1)

    # 3. Update routing rules
    rules = [
        ('a307fb7d81d841e5a2fd94ca785df944', 'Forward scott@ to owner', 'scott@premierpouredwalls.com'),
        ('850f4118935a49699a64fdf5ba9083aa', 'Forward info@ to owner', 'info@premierpouredwalls.com')
    ]

    for rule_id, name, from_addr in rules:
        payload = {
            'matchers': [{'type': 'literal', 'field': 'to', 'value': from_addr}],
            'actions': [{'type': 'forward', 'value': [target_email]}],
            'name': name,
            'enabled': True
        }
        rule_req = urllib.request.Request(
            f'https://api.cloudflare.com/client/v4/zones/{zone_id}/email/routing/rules/{rule_id}',
            data=json.dumps(payload).encode('utf-8'),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            method='PUT'
        )
        resp = urllib.request.urlopen(rule_req)
        print(f"✓ Updated rule '{name}' -> forwarding to {target_email} (HTTP {resp.status})")

    print("\n✅ All email routing rules successfully pointing to premierpouredwalls@gmail.com!")

if __name__ == '__main__':
    main()
