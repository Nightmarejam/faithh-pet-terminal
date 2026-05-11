# G0 Account Lockdown Checklist

## Items to complete at account.microsoft.com/security

- [ ] Sign out all sessions (Security > Recent activity > Sign out everywhere)
- [ ] Change password (long passphrase, unique, not reused anywhere)
- [ ] Microsoft Authenticator confirmed as primary 2FA
- [ ] Remove any unknown phone numbers or email recovery methods
- [ ] Check and remove unknown trusted devices
- [ ] Verify no unknown aliases at account.microsoft.com > Your info > Aliases

## Items to complete in Outlook web (outlook.live.com > Settings)

- [ ] Mail forwarding: confirm no forwarding to external addresses
- [ ] Rules: review all inbox rules, delete unknown ones
- [ ] Connected apps: revoke access for any unrecognized apps

## Cascade action

After operator confirms above items complete, create artifact:
`reports/security/G0_account_lockdown_complete_YYYYMMDD.md`
with a brief confirmation note and date.
