nescient
====================
python tkinter chat server
-------------------------


local network falcon chat server and tkinter client side chat UI

litepresence2020

to serve to www, go to http://192.168.0.1 ROUTER settings page in browswer, then:

IPV6 Firewall ALLOW:

    `HTTP IN`
    `HTTPS IN`

"Port Forwarding", bind your LAN to your WAN:

your machine's LAN address is something like 192.168.0.2; 0.3 0.4 etc.; you can do:

    `hostname -I`

Router Port Forwarding setting Should be something like:

`Network     IP              MINPORT MAXPORT`

`LAN IP      192.168.0.2     8000 8000`

`WAN IP      0.0.0.0         26016 27019`

When client attaches from WWW update their IP and PORT to your external IP
you can get that at www.myip.com

When serving to WWW

`IP = WAN_IP`
`PORT = 27016`

When serving locally

`IP = LAN_IP #192.168.0.2; 0.3 0.4 etc. your LAN IP`
`PORT = 8000 #8001, etc.`

