#!/usr/bin/perl
use strict;
use warnings;

my $file = "$ARGV[0]";
open my $fh, '<', $file or die "Can't open $file: $!";
my $content = do { local $/; <$fh> };
close $fh;

my $search = 'for (const \[service, status\] of Object\.entries\(data\.services\))';
my $replace = <<'JS';
for (const [service, info] of Object.entries(data.services)) {
    const statusValue = info.status || "unknown";
    const isOnline = statusValue === "online" || statusValue === "configured";
    const statusIcon = isOnline ? "Filled Circle" : "Empty Circle";
    const statusColor = isOnline ? "" : "style=\"color: #ff6666;\"";
    statusItem.innerHTML = `<span class="status-name">\${service}</span><span class="status-value" \${statusColor}>\${statusIcon} \${statusValue.toUpperCase()}</span>`;
}
JS

$content =~ s/\Q$search\E/$replace/s;

open $fh, '>', $file or die "Can't write $file: $!";
print $fh $content;
close $fh;

print "Status loop patched successfully!\n";
