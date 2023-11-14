#!/usr/bin/env bash

install_dependencies() {
  poetry install
}

update_dependencies() {
  poetry update
}

show_dependencies() {
  # echo -en '\n Showing installed dependencies . . . \n'
  echo -e "\n###########################################################"
  echo "Showing installed dependencies . . ."
  echo "###########################################################"
  poetry show
}

pre_commit_hooks() {
  echo -e "\n###########################################################"
  echo "Installing pre-commit and pre-push hooks . . ."
  echo "###########################################################"
  poetry run pre-commit install --hook-type pre-commit
  poetry run pre-commit install --hook-type pre-push
}

pre_commit_autoupdate() {
  echo -en '\n pre-commit autoupdate . . . \n'
  poetry run pre-commit autoupdate
}

poetry_init() {
  install_dependencies
  show_dependencies
  pre_commit_hooks
}

poetry_init

$SHELL
