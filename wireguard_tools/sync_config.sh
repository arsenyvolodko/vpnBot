#!/bin/bash

wg-quick down "$1"
wg-quick up "$1"