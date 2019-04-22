#!/bin/bash

grep '^\s*'"$1"'=' "${2}"|cut -d'=' -f2-
