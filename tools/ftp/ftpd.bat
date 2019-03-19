@echo off
rem @author dhacky
rem @email dhgacky@gmail.com
rem @date 2016/07
rem @version 1.0

set host=%1
set user=%2
set pwd=%3

if {%host%}=={} goto usage
if {%user%}=={} goto usage
if {%pwd%}=={} goto usage

echo Start connect ftp server %host%
title %host%
set ftpFile=autoftp.ftp
echo open %host% > %ftpFile%
echo user %user% %pwd% >> %ftpFile%
rem echo cd upload >> %ftpFile%
echo prompt >> %ftpFile%
echo mput %uploadFiles% >> %ftpFile%
echo quit >> %ftpFile%
ftp -n -s:%ftpFile%
del /f/q %ftpFile% > nul
echo upload files OK
echo;
title cmd
goto end

:usage
echo usage: ftpd host user pwd
:end