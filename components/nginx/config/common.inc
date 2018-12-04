# Global configuration common to all sites.
# Generated from template; don't edit manually!

# Ensure canonical hostname
if ($host != $server_name) {
    rewrite (.*) https://$server_name$1 permanent;
}

# disallow hidden files (and prevent various path-based attacks)
location ~ /\. {
    deny all;
    access_log off;
    log_not_found off;
}

# the following standard files may not exists
location = /favicon.ico {
    log_not_found off;
}

location = /robots.txt {
    allow all;
    log_not_found off;
}

# vim: set ft=nginx sts=4 sw=4 et:
