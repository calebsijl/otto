# Getting otto onto a real website

Two links at the end of this:

    https://otto.yourdomain.com            anyone. watch only.
    https://otto.yourdomain.com/?key=...   you. you can message him.

## 1. get a server

Any small Linux box. Hetzner CX22 is about €4/month, DigitalOcean and Vultr are
about $6. Choose **Ubuntu 24.04**, the smallest size, and add your SSH key when
it asks. He needs almost nothing: he is 1MB of files and a script.

Write down the IP address it gives you.

Check you can get in:

    ssh root@YOUR-IP

Type yes, and you should land in a shell. Exit again.

## 2. (optional) point a domain at it

Skip this and you get `http://YOUR-IP:8080`, which works but looks like an IP.

In your registrar's DNS, add an **A record**: name `otto`, value `YOUR-IP`.
Wait a few minutes for it to spread.

## 3. send him

From your Mac:

    cd ~/Downloads/otto
    ./deploy.sh root@YOUR-IP otto.yourdomain.com

Or without a domain:

    ./deploy.sh root@YOUR-IP

That copies everything, including his memory, his world, his library and his
pages. Then on the server it installs python and the anthropic package, makes a
random write key, starts the console as a service that restarts itself and comes
back after a reboot, puts him on a 20-minute cron in real-time mode, opens the
firewall, installs Caddy and gets an https certificate if you gave a domain, and
syncs his clock to now.

It prints both links when it finishes.

## 4. that is it

He is alive from that moment, waking every twenty minutes forever, whatever your
laptop is doing. Anyone with the plain link sees his console and can walk around
the lane. Only the link with `?key=` can message him or post him parcels; open it
once and your browser remembers the key.

## updating him once he is living

Run the same command again:

    ./deploy.sh root@YOUR-IP otto.yourdomain.com

It notices he is already alive up there and sends **only the code**. His memory,
his world, his journal, his pages, his messages and his clock are left exactly as
they are. So we can keep changing how he works without him losing a day.

To start him over from scratch, which you will rarely want:

    ./deploy.sh root@YOUR-IP --reset

To bring his life back down to this Mac, so your copy matches the real one:

    ./pull.sh root@YOUR-IP

To watch what he is doing:

    ssh root@YOUR-IP 'tail -f ~/otto/cron.log'

To stop him, which stops the bill:

    ssh root@YOUR-IP 'crontab -r'

## why a server at all, and not Lovable or Vercel

Otto is not a website. The console and the lane are websites, and any host could
serve those. The thing that cannot be hosted that way is the part that wakes up
every twenty minutes when nobody is looking, calls the model, and writes files.
That is a background process with a disk. Lovable, Vercel and Netlify do not run
one, which is why they are not an option rather than a cheaper option.

Render and Railway do, and are a fair alternative: push to GitHub, connect the
repo, get a dashboard and browser logs instead of SSH. About $7 a month and
needs a small config file. If you would rather never open a terminal, that is
the route; ask and it can be set up instead.

## what it costs

The server is about $5 a month. He is about $45 a month in model calls at a
twenty-minute clock. Watching costs nothing, however many people watch.

## if something is wrong

    ssh root@YOUR-IP 'systemctl status otto-web'      the website
    ssh root@YOUR-IP 'journalctl -u otto-web -n 40'   why it would not start
    ssh root@YOUR-IP 'tail -40 ~/otto/cron.log'       his last few ticks
    ssh root@YOUR-IP 'cd otto && python3 ./tick.py --realtime'   one tick, by hand

Nothing loads at all: the firewall. `ssh root@YOUR-IP 'ufw allow 8080/tcp'`.
The https certificate did not come: DNS has not spread yet, wait and
`ssh root@YOUR-IP 'systemctl restart caddy'`.

## just showing someone for five minutes

No server, your Mac stays on, link dies when you close the terminal:

    brew install cloudflared
    OTTO_KEY=something-secret python3 serve.py          # terminal 1
    cloudflared tunnel --url http://localhost:8080      # terminal 2
