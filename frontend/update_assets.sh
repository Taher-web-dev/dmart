#!/bin/bash
cp ./node_modules/bootstrap/dist/css/bootstrap.min.css* ./assets/
ls -alh assets/bootstrap.min.css assets/bootstrap.min.css.map
cp ./node_modules/bootstrap/dist/css/bootstrap.rtl.min.css* ./assets/ 
ls -alh assets/bootstrap.rtl.min.css assets/bootstrap.rtl.min.css.map
cp ./node_modules/bootstrap-icons/font/bootstrap-icons.css ./assets/
ls -alh assets/bootstrap-icons.css
cp ./node_modules/bootstrap-icons/font/fonts/bootstrap-icons.woff* ./assets/fonts/
ls -alh assets/fonts/bootstrap-icons.woff assets/fonts/bootstrap-icons.woff2
