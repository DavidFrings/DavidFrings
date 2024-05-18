# Setup for MC Velocity Server

````bash
sudo apt install openjdk-17-jdk-headless && java -version
````

````bash
sudo apt update && sudo apt upgrade
````

````bash
mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/ && mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/ & mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-1/ & mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-2/ & mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-3/ & mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/lobby/ & mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/survival/ & mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/test-world/
````

````bash
nano /home/server/games/minecraft.sh
````

Insert:

````bash
#!/bin/bash

if sudo screen -list | grep -q "velocity"; then
    sudo /mnt/Festplatte/Server/Minecraft/Server9-Velocity/connect-minecraft.sh
else
    sudo /mnt/Festplatte/Server/Minecraft/Server9-Velocity/start-minecraft.sh
fi
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/connect-minecraft.sh
````

Insert:

````bash
#!/bin/bash

#sudo screen -list
read -p "Please select between: Velocity[0], Project 1[1], Project 2[2], Project 3[3], Lobby[4], Survival[5], Test World[6] & Kill all[9] (Use kill only in Emergency): " server

if [ $server = "Velocity" ] || [ $server = "0" ]; then
        sudo screen -r velocity
else if [ $server = "Project 1" ] || [ $server = "1" ]; then
        sudo screen -r project-1
else if [ $server = "Project 2" ] || [ $server = "2" ]; then
        sudo screen -r project-2
else if [ $server = "Project 3" ] || [ $server = "3" ]; then
        sudo screen -r project-3
else if [ $server = "Lobby" ] || [ $server = "4" ]; then
        sudo screen -r lobby
else if [ $server = "Survival" ] || [ $server = "5" ]; then
        sudo screen -r survival
else if [ $server = "Test World" ] || [ $server = "6" ]; then
        sudo screen -r test-world
else if [ $server = "Kill all" ] || [ $server = "9" ]; then
        #Abfrage hinzufügen!!!
        sudo pkill screen
fi fi fi fi fi fi fi fi
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/start-minecraft.sh
````

````bash
chmod u+x start.sh
````

Insert:

````bash
#!/bin/bash

/mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/screen-create.sh
/mnt/Festplatte/Server/Minecraft/Server9-Velocity/lobby/screen-create.sh

function sel {
    read -p "Please select between: Project 1[1], Project 2[2], Project 3[3], Survival[5], Test World [6] & End[9]: " server  
    if [ $server = "End" ] || [ $server = "0" ]; then
                exit 1
        else if [ $server = "Project 1" ] || [ $server = "1" ]; then
                /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-1/screen-create.sh
                sel
        else if [ $server = "Project 2" ] || [ $server = "2" ]; then
                /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-2/screen-create.sh
                sel
        else if [ $server = "Project 3" ] || [ $server = "3" ]; then
                /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-3/screen-create.sh
                sel
        else if [ $server = "Survival" ] || [ $server = "5" ]; then
                /mnt/Festplatte/Server/Minecraft/Server9-Velocity/survival/screen-create.sh
                sel
        else if [ $server = "Test World" ] || [ $server = "6" ]; then
                /mnt/Festplatte/Server/Minecraft/Server9-Velocity/test-world/screen-create.sh
                sel
        fi fi fi fi fi fi
}

sel
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d velocity

sleep 5
screen -S velocity -X stuff 'cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/\n'
screen -S velocity -X stuff './start.sh\n'
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-1/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d project-1

sleep 5
screen -S project-1 -X stuff 'cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-1/\n'
screen -S project-1 -X stuff './start.sh\n'
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-2/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d project-2

sleep 5
screen -S project-2 -X stuff 'cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-2/\n'
screen -S project-2 -X stuff './start.sh\n'
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-3/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d project-3

sleep 5
screen -S project-3 -X stuff 'cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-3/\n'
screen -S project-3 -X stuff './start.sh\n'
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/lobby/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d lobby

sleep 5
screen -S lobby -X stuff 'cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/lobby/\n'
screen -S lobby -X stuff './start.sh\n'
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/survival/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d survival

sleep 5
screen -S survival -X stuff 'cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/survival/\n'
screen -S survival -X stuff './start.sh\n'
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/test-world/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d test-world

sleep 5
screen -S test-world -X stuff 'cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/test-world/\n'
screen -S test-world -X stuff './start.sh\n'
````

````bash
chmod u+x start.sh
````

## Configer all Servers

````bash
cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/ && wget https://api.papermc.io/v2/projects/velocity/versions/3.3.0-SNAPSHOT/builds/390/downloads/velocity-3.3.0-SNAPSHOT-390.jar
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/start.sh
````

Insert:

````bash
#!/bin/bash

java -Xms1G -Xmx20G -XX:+UseG1GC -XX:G1HeapRegionSize=4M -XX:+UnlockExperimentalVMOptions -XX:+ParallelRefProcEnabled -XX:+AlwaysPreTouch -XX:MaxInlineLevel=15 -jar velocity-3.3.0-SNAPSHOT-390.jar
````

````bash
chmod u+x start.sh
````

````bash
nano /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/velocity.toml
````

Insert:

````toml
# Config version. Do not change this
config-version = "2.7"

# What port should the proxy be bound to? By default, we'll bind to all addresses on port 25577.
bind = "0.0.0.0:25565"

# What should be the MOTD? This gets displayed when the player adds your server to
# their server list. Only MiniMessage format is accepted.
motd = "<#09add3>PrivatGames.net"

# What should we display for the maximum number of players? (Velocity does not support a cap
# on the number of players online.)
show-max-players = 420

# Should we authenticate players with Mojang? By default, this is on.
online-mode = true

# Should the proxy enforce the new public key security standard? By default, this is on.
force-key-authentication = true

# If client's ISP/AS sent from this proxy is different from the one from Mojang's
# authentication server, the player is kicked. This disallows some VPN and proxy
# connections but is a weak form of protection.
prevent-client-proxy-connections = false

# Should we forward IP addresses and other data to backend servers?
# Available options:
# - "none":        No forwarding will be done. All players will appear to be connecting
#                  from the proxy and will have offline-mode UUIDs.
# - "legacy":      Forward player IPs and UUIDs in a BungeeCord-compatible format. Use this
#                  if you run servers using Minecraft 1.12 or lower.
# - "bungeeguard": Forward player IPs and UUIDs in a format supported by the BungeeGuard
#                  plugin. Use this if you run servers using Minecraft 1.12 or lower, and are
#                  unable to implement network level firewalling (on a shared host).
# - "modern":      Forward player IPs and UUIDs as part of the login process using
#                  Velocity's native forwarding. Only applicable for Minecraft 1.13 or higher.
player-info-forwarding-mode = "NONE"

# If you are using modern or BungeeGuard IP forwarding, configure a file that contains a unique secret here.
# The file is expected to be UTF-8 encoded and not empty.
forwarding-secret-file = "forwarding.secret"

# Announce whether or not your server supports Forge. If you run a modded server, we
# suggest turning this on.
# 
# If your network runs one modpack consistently, consider using ping-passthrough = "mods"
# instead for a nicer display in the server list.
announce-forge = false

# If enabled (default is false) and the proxy is in online mode, Velocity will kick
# any existing player who is online if a duplicate connection attempt is made.
kick-existing-players = true

# Should Velocity pass server list ping requests to a backend server?
# Available options:
# - "disabled":    No pass-through will be done. The velocity.toml and server-icon.png
#                  will determine the initial server list ping response.
# - "mods":        Passes only the mod list from your backend server into the response.
#                  The first server in your try list (or forced host) with a mod list will be
#                  used. If no backend servers can be contacted, Velocity won't display any
#                  mod information.
# - "description": Uses the description and mod list from the backend server. The first
#                  server in the try (or forced host) list that responds is used for the
#                  description and mod list.
# - "all":         Uses the backend server's response as the proxy response. The Velocity
#                  configuration is used if no servers could be contacted.
ping-passthrough = "ALL"

# If not enabled (default is true) player IP addresses will be replaced by <ip address withheld> in logs
enable-player-address-logging = true

[servers]
# Configure your servers here. Each key represents the server's name, and the value
# represents the IP address of the server to connect to.
lobby = "127.0.0.1:30066"
project-1 = "127.0.0.1:30067"
project-2 = "127.0.0.1:30068"
project-3 = "127.0.0.1:30069"
survival = "127.0.0.1:30070"
test-world = "127.0.0.1:30071"

# In what order we should try servers when a player logs in or is kicked from a server.
try = [
    "lobby"
]

[forced-hosts]
# Configure your forced hosts here.
"lobby.privatgames.net" = [
    "lobby"
]
"project-1.privatgames.net" = [
    "project-2"
]
"project-2.privatgames.net" = [
    "project-2"
]
"project-3.privatgames.net" = [
    "project-3"
]
"survival.privatgames.net" = [
    "survival"
]
"test-world.privatgames.net" = [
    "test-world"
]

[advanced]
# How large a Minecraft packet has to be before we compress it. Setting this to zero will
# compress all packets, and setting it to -1 will disable compression entirely.
compression-threshold = 256

# How much compression should be done (from 0-9). The default is -1, which uses the
# default level of 6.
compression-level = -1

# How fast (in milliseconds) are clients allowed to connect after the last connection? By
# default, this is three seconds. Disable this by setting this to 0.
login-ratelimit = 3000

# Specify a custom timeout for connection timeouts here. The default is five seconds.
connection-timeout = 5000

# Specify a read timeout for connections here. The default is 30 seconds.
read-timeout = 30000

# Enables compatibility with HAProxy's PROXY protocol. If you don't know what this is for, then
# don't enable it.
haproxy-protocol = false

# Enables TCP fast open support on the proxy. Requires the proxy to run on Linux.
tcp-fast-open = true

# Enables BungeeCord plugin messaging channel support on Velocity.
bungee-plugin-message-channel = true

# Shows ping requests to the proxy from clients.
show-ping-requests = true

# By default, Velocity will attempt to gracefully handle situations where the user unexpectedly
# loses connection to the server without an explicit disconnect message by attempting to fall the
# user back, except in the case of read timeouts. BungeeCord will disconnect the user instead. You
# can disable this setting to use the BungeeCord behavior.
failover-on-unexpected-server-disconnect = true

# Declares the proxy commands to 1.13+ clients.
announce-proxy-commands = true

# Enables the logging of commands
log-command-executions = true

# Enables logging of player connections when connecting to the proxy, switching servers
# and disconnecting from the proxy.
log-player-connections = true

# Allows players transferred from other hosts via the
# Transfer packet (Minecraft 1.20.5) to be received.
accepts-transfers = true

[query]
# Whether to enable responding to GameSpy 4 query responses or not.
enabled = false

# If query is enabled, on what port should the query protocol listen on?
port = 25565

# This is the map name that is reported to the query services.
map = "Velocity"

# Whether plugins should be shown in query response by default or not
show-plugins = false
````

### Secure Velocity with BungeeGuard

````bash
cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/plugins/ && wget https://github.com/lucko/BungeeGuard/releases/download/v1.3.3/BungeeGuard.jar && mkdir /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/plugins/BungeeGuard && echo 'TWY6fiZc8YaiJQyvBNwOlr1OWf75tiqDG4YrEhZXYY0mah1nyWIbbKGXizPXVrsZ' > /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/plugins/BungeeGuard/token.yml && cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/velocity/plugins/ && wget https://hangarcdn.papermc.io/plugins/ViaVersion/ViaVersion/versions/4.10.2/PAPER/ViaVersion-4.10.2.jar
````

### Setup Game Servers

````bash
cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/lobby/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-1/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-2/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/project-3/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/survival/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd /mnt/Festplatte/Server/Minecraft/Server9-Velocity/test-world/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy