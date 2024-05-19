# Setup for MC Velocity Server

````bash
sudo apt install openjdk-17-jdk-headless && java -version
````

````bash
sudo apt update && sudo apt upgrade
````

````bash
mkdir ~/test/ && mkdir ~/test/velocity/ & mkdir ~/test/project-1/ & mkdir ~/test/project-2/ & mkdir ~/test/project-3/ & mkdir ~/test/lobby/ & mkdir ~/test/survival/ & mkdir ~/test/test-world/ && nano ~/test/minecraft.sh && chmod u+x ~/test/minecraft.sh
````

Insert:

````bash
#!/bin/bash

if sudo screen -list | grep -q "velocity"; then
    sudo ~/test/connect-minecraft.sh
else
    sudo ~/test/start-minecraft.sh
fi
````

````bash
nano ~/test/connect-minecraft.sh && chmod u+x ~/test/connect-minecraft.sh
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
nano ~/test/start-minecraft.sh && chmod u+x ~/test/start-minecraft.sh
````

Insert:

````bash
#!/bin/bash

~/test/velocity/screen-create.sh
~/test/lobby/screen-create.sh

function sel {
    read -p "Please select between: Project 1[1], Project 2[2], Project 3[3], Survival[5], Test World [6] & End[9]: " server  
    if [ $server = "End" ] || [ $server = "0" ]; then
                exit 1
        else if [ $server = "Project 1" ] || [ $server = "1" ]; then
                ~/test/project-1/screen-create.sh
                sel
        else if [ $server = "Project 2" ] || [ $server = "2" ]; then
                ~/test/project-2/screen-create.sh
                sel
        else if [ $server = "Project 3" ] || [ $server = "3" ]; then
                ~/test/project-3/screen-create.sh
                sel
        else if [ $server = "Survival" ] || [ $server = "5" ]; then
                ~/test/survival/screen-create.sh
                sel
        else if [ $server = "Test World" ] || [ $server = "6" ]; then
                ~/test/test-world/screen-create.sh
                sel
        fi fi fi fi fi fi
}

sel
````

````bash
nano ~/test/velocity/screen-create.sh && chmod u+x ~/test/velocity/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d velocity

sleep 5
screen -S velocity -X stuff 'cd ~/test/velocity/\n'
screen -S velocity -X stuff './start.sh\n'
````

````bash
nano ~/test/project-1/screen-create.sh && chmod u+x ~/test/project-1/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d project-1

sleep 5
screen -S project-1 -X stuff 'cd ~/test/project-1/\n'
screen -S project-1 -X stuff './start.sh\n'
````

````bash
nano ~/test/project-2/screen-create.sh && chmod u+x ~/test/project-2/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d project-2

sleep 5
screen -S project-2 -X stuff 'cd ~/test/project-2/\n'
screen -S project-2 -X stuff './start.sh\n'
````

````bash
nano ~/test/project-3/screen-create.sh && chmod u+x ~/test/project-3/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d project-3

sleep 5
screen -S project-3 -X stuff 'cd ~/test/project-3/\n'
screen -S project-3 -X stuff './start.sh\n'
````

````bash
nano ~/test/lobby/screen-create.sh && chmod u+x ~/test/lobby/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d lobby

sleep 5
screen -S lobby -X stuff 'cd ~/test/lobby/\n'
screen -S lobby -X stuff './start.sh\n'
````

````bash
nano ~/test/survival/screen-create.sh && chmod u+x ~/test/survival/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d survival

sleep 5
screen -S survival -X stuff 'cd ~/test/survival/\n'
screen -S survival -X stuff './start.sh\n'
````

````bash
nano ~/test/test-world/screen-create.sh && chmod u+x ~/test/test-world/screen-create.sh
````

Insert:

````bash
#!/bin/bash

screen -m -d test-world

sleep 5
screen -S test-world -X stuff 'cd ~/test/test-world/\n'
screen -S test-world -X stuff './start.sh\n'
````

## Configer all Servers

````bash
cd ~/test/velocity/ && wget https://api.papermc.io/v2/projects/velocity/versions/3.3.0-SNAPSHOT/builds/390/downloads/velocity-3.3.0-SNAPSHOT-390.jar && nano ~/test/velocity/start.sh && chmod u+x ~/test/velocity/start.sh
````

Insert:

````bash
#!/bin/bash

java -Xms1G -Xmx20G -XX:+UseG1GC -XX:G1HeapRegionSize=4M -XX:+UnlockExperimentalVMOptions -XX:+ParallelRefProcEnabled -XX:+AlwaysPreTouch -XX:MaxInlineLevel=15 -jar velocity-3.3.0-SNAPSHOT-390.jar
````

````bash
nano ~/test/velocity/velocity.toml
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
player-info-forwarding-mode = "bungeeguard"

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
cd ~/test/velocity/plugins/ && wget https://github.com/lucko/BungeeGuard/releases/download/v1.3.3/BungeeGuard.jar && mkdir ~/test/velocity/plugins/BungeeGuard && echo 'TWY6fiZc8YaiJQyvBNwOlr1OWf75tiqDG4YrEhZXYY0mah1nyWIbbKGXizPXVrsZ' > ~/test/velocity/plugins/BungeeGuard/token.yml && cd ~/test/velocity/plugins/ && wget https://hangarcdn.papermc.io/plugins/ViaVersion/ViaVersion/versions/4.10.2/PAPER/ViaVersion-4.10.2.jar
````

### Setup Game Servers

````bash
cd ~/test/lobby/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt && mkdir ~/test/lobby/plugins/ && mkdir ~/test/lobby/plugins/BungeeGuard && nano ~/test/lobby/start.sh && chmod u+x ~/test/lobby/start.sh
````

Insert:

````bash
#!/bin/bash

java -Xms1G -Xmx20G -jar paper-1.20.4-496.jar --nogui
````

````bash
nano ~/test/lobby/server.properties
````

Insert:

````toml
enable-jmx-monitoring=false
level-seed=
rcon.port=25575
enable-command-block=false
gamemode=survival
enable-query=false
generator-settings={}
enforce-secure-profile=true
level-name=world
motd=motd
query.port=30066
pvp=true
generate-structures=true
max-chained-neighbor-updates=1000000
difficulty=hard
network-compression-threshold=256
max-tick-time=60000
require-resource-pack=false
max-players=42
use-native-transport=true
enable-status=true
online-mode=false
allow-flight=false
initial-disabled-packs=
broadcast-rcon-to-ops=true
view-distance=20
resource-pack-prompt=
server-ip=
allow-nether=true
server-port=30066
enable-rcon=false
sync-chunk-writes=true
op-permission-level=4
prevent-proxy-connections=false
hide-online-players=false
resource-pack=
entity-broadcast-range-percentage=100
simulation-distance=15
player-idle-timeout=0
rcon.password=
debug=false
force-gamemode=false
rate-limit=0
hardcore=false
white-list=false
broadcast-console-to-ops=true
spawn-npcs=true
spawn-animals=true
log-ips=true
function-permission-level=2
initial-enabled-packs=vanilla
level-type=minecraft\:normal
text-filtering-config=
spawn-monsters=true
enforce-whitelist=false
resource-pack-sha1=
spawn-protection=1
max-world-size=29999984
````

````bash
nano ~/test/lobby/spigot.yml
````

Insert:

````yml
# This is the main configuration file for Spigot.
# As you can see, there's tons to configure. Some options may impact gameplay, so use
# with caution, and make sure you know what each option does before configuring.
# For a reference for any variable inside this file, check out the Spigot wiki at
# http://www.spigotmc.org/wiki/spigot-configuration/
#
# If you need help with the configuration or have any questions related to Spigot,
# join us at the Discord or drop by our forums and leave a post.
#
# Discord: https://www.spigotmc.org/go/discord
# Forums: http://www.spigotmc.org/

settings:
  debug: false
  timeout-time: 60
  restart-on-crash: true
  restart-script: ./start.sh
  bungeecord: true
  save-user-cache-on-stop-only: false
  log-villager-deaths: true
  log-named-deaths: true
  moved-wrongly-threshold: 0.0625
  moved-too-quickly-multiplier: 10.0
  player-shuffle: 0
  user-cache-size: 1000
  netty-threads: 4
  attribute:
    maxHealth:
      max: 2048.0
    movementSpeed:
      max: 2048.0
    attackDamage:
      max: 2048.0
  sample-count: 12
advancements:
  disable-saving: false
  disabled:
  - minecraft:story/disabled
messages:
  restart: Server is restarting
  whitelist: You are not whitelisted on this server!
  unknown-command: Unknown command. Type "/help" for help.
  server-full: The server is full!
  outdated-client: Outdated client! Please use {0}
  outdated-server: Outdated server! I'm still on {0}
world-settings:
  default:
    below-zero-generation-in-existing-chunks: true
    wither-spawn-sound-radius: 0
    hanging-tick-frequency: 100
    dragon-death-sound-radius: 0
    end-portal-sound-radius: 0
    zombie-aggressive-towards-villager: true
    enable-zombie-pigmen-portal-spawns: true
    mob-spawn-range: 8
    simulation-distance: default
    item-despawn-rate: 6000
    arrow-despawn-rate: 1200
    trident-despawn-rate: 1200
    nerf-spawner-mobs: false
    view-distance: default
    entity-activation-range:
      animals: 32
      monsters: 32
      raiders: 48
      misc: 16
      water: 16
      villagers: 32
      flying-monsters: 32
      wake-up-inactive:
        animals-max-per-tick: 4
        animals-every: 1200
        animals-for: 100
        monsters-max-per-tick: 8
        monsters-every: 400
        monsters-for: 100
        villagers-max-per-tick: 4
        villagers-every: 600
        villagers-for: 100
        flying-monsters-max-per-tick: 8
        flying-monsters-every: 200
        flying-monsters-for: 100
      villagers-work-immunity-after: 100
      villagers-work-immunity-for: 20
      villagers-active-for-panic: true
      tick-inactive-villagers: true
      ignore-spectators: false
    growth:
      cactus-modifier: 100
      cane-modifier: 100
      melon-modifier: 100
      mushroom-modifier: 100
      pumpkin-modifier: 100
      sapling-modifier: 100
      beetroot-modifier: 100
      carrot-modifier: 100
      potato-modifier: 100
      torchflower-modifier: 100
      wheat-modifier: 100
      netherwart-modifier: 100
      vine-modifier: 100
      cocoa-modifier: 100
      bamboo-modifier: 100
      sweetberry-modifier: 100
      kelp-modifier: 100
      twistingvines-modifier: 100
      weepingvines-modifier: 100
      cavevines-modifier: 100
      glowberry-modifier: 100
      pitcherplant-modifier: 100
    max-tnt-per-tick: 100
    seed-village: 10387312
    seed-desert: 14357617
    seed-igloo: 14357618
    seed-jungle: 14357619
    seed-swamp: 14357620
    seed-monument: 10387313
    seed-shipwreck: 165745295
    seed-ocean: 14357621
    seed-outpost: 165745296
    seed-endcity: 10387313
    seed-slime: 987234911
    seed-nether: 30084232
    seed-mansion: 10387319
    seed-fossil: 14357921
    seed-portal: 34222645
    seed-ancientcity: 20083232
    seed-trailruins: 83469867
    seed-buriedtreasure: 10387320
    seed-mineshaft: default
    seed-stronghold: default
    thunder-chance: 100000
    max-tick-time:
      tile: 50
      entity: 50
    entity-tracking-range:
      players: 48
      animals: 48
      monsters: 48
      misc: 32
      display: 128
      other: 64
    merge-radius:
      item: 2.5
      exp: 3.0
    hunger:
      jump-walk-exhaustion: 0.05
      jump-sprint-exhaustion: 0.2
      combat-exhaustion: 0.1
      regen-exhaustion: 6.0
      swim-multiplier: 0.01
      sprint-multiplier: 0.1
      other-multiplier: 0.0
    ticks-per:
      hopper-transfer: 8
      hopper-check: 1
    hopper-amount: 1
    hopper-can-load-chunks: false
    verbose: false
players:
  disable-saving: false
commands:
  silent-commandblock-console: false
  replace-commands:
  - setblock
  - summon
  - testforblock
  - tellraw
  log: true
  spam-exclusions:
  - /skill
  tab-complete: 0
  send-namespaced: true
config-version: 12
stats:
  disable-saving: false
  forced-stats: {}

````

````bash
nano ~/test/lobby/plugins/BungeeGuard/config.yml
````

Insert:

````yml
# BungeeGuard Configuration

# Allowed authentication tokens.
allowed-tokens:
  - "TWY6fiZc8YaiJQyvBNwOlr1OWf75tiqDG4YrEhZXYY0mah1nyWIbbKGXizPXVrsZ"

# Messages

# Kick message sent to connections without any forwarded data from the proxy.
# Most likely a vanilla client connecting directly to the server, bypassing the proxy.
no-data-kick-message: "&cUnable to authenticate - no data was forwarded by the proxy."

# Kick message sent to connections with forwarding data, but without a correct BungeeGuard token
# included in their handshake. Assuming BungeeGuard is installed correctly on all proxies,
# this is most likely a client trying to exploit the BungeeCord protocol to spoof their uuid.
invalid-token-kick-message: "&cUnable to authenticate."
````

````bash
chmod u+x ~/test/lobby/start.sh  && cd ~/test/lobby/plugins/ && wget https://github.com/lucko/BungeeGuard/releases/download/v1.3.3/BungeeGuard.jar&& cd ~/test/lobby/plugins/ && wget https://hangarcdn.papermc.io/plugins/ViaVersion/ViaVersion/versions/4.10.2/PAPER/ViaVersion-4.10.2.jar
````

1

````bash
cd ~/test/project-1/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd ~/test/project-2/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd ~/test/project-3/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd ~/test/survival/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy

````bash
cd ~/test/test-world/ && wget https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar && echo 'eula=true' > eula.txt
````

Setup config for Veloctiy
