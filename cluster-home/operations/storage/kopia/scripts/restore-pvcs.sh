#!/usr/bin/env sh
buvisctl restore -n security authentik
buvisctl restore -n gtd linkace-db
buvisctl restore -n gtd monica-db
buvisctl restore -n gtd monica-config
buvisctl restore -n smarthome hass-config
buvisctl restore -n radio mopidy-data
buvisctl restore -n media prowlarr-config
buvisctl restore -n media qbittorrent-config
buvisctl restore -n media nzbget-config
buvisctl restore -n media bazarr-config
buvisctl restore -n media lidarr-config
buvisctl restore -n media radarr-config
buvisctl restore -n media sonarr-config
buvisctl restore -n media jellyfin-data
buvisctl restore -n media jellyseerr-config
buvisctl restore -n media tdarr-data
buvisctl restore -n media tdarr-config
