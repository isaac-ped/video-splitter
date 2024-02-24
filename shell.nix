{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.hello
    pkgs.poetry
    pkgs.python310
    pkgs.ffmpeg

    # keep this line if you use bash
    pkgs.bashInteractive
  ];
}
