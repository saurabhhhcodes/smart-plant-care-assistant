{ pkgs }: {
  deps = [
    pkgs.python39
    pkgs.python39Packages.flask
    pkgs.python39Packages.opencv4
    pkgs.python39Packages.numpy
    pkgs.python39Packages.pillow
    pkgs.python39Packages.flask-cors
  ];
}
