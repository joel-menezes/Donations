# Add `/etc/secrets/firebase.json` to `.gitignore`
with open(".gitignore", "a+") as f:
    f.seek(0)
    lines = f.read().splitlines()
    if "/etc/secrets/firebase.json" not in lines:
        f.write("\n/etc/secrets/firebase.json\n")
