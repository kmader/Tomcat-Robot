#!/usr/bin/perl -w

#$Header: /cvs/X/ROBOT/X02DA/App/scripts/X_ROBOT_X02DA_robotSMS.pl,v 1.2 2008/12/02 16:33:33 mader Exp $
use Net::SMTP; 
use POSIX qw(strftime);

$now_string = strftime "%D %T", gmtime;
$phone_num=$ARGV[0] . '@sms.switch.ch';
$hn=qx/hostname --fqdn/;
chomp($hn);
$smtp = Net::SMTP->new("mailsend.psi.ch");

$smtp->mail('kevin.mader@psi.ch');
$smtp->to($phone_num, { SkipBad => 1 });

$smtp->data();
$smtp->datasend("Subject: " . $ARGV[1] . "\n");
$smtp->datasend('From: TomcatBeamline' . "\n");
$smtp->datasend("Date: " . $now_string . "\n");
$smtp->datasend("To: " . $phone_num);
$smtp->datasend("\n" . $ARGV[1] . "\n");
$smtp->dataend();
$smtp->quit;
sleep 2;
exit;
