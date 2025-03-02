{
  description = "A basic flake demoing a python wrapper with lib injection";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    supportedSystems = ["x86_64-linux"];
    forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    pkgs = forAllSystems (system: import nixpkgs {inherit system;});
    pythonVer = "311";
  in {
    packages = {};

    devShells = forAllSystems (system:
      with pkgs.${system}; let
        python = pkgs.${system}."python${pythonVer}";
        wrappedPython = writeShellScriptBin "python" ''
          export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH
          SCRIPT_DIR=$(${coreutils}/bin/dirname $(${coreutils}/bin/realpath -s "$0"))
          exec -a "$SCRIPT_DIR/python" "${python}/bin/python" "$@"
        '';
      in
        with pkgs.${system}; {
          default = pkgs.${system}.mkShell {
            # adapt to your needs
            NIX_LD_LIBRARY_PATH =
              lib.makeLibraryPath [stdenv.cc.cc openssl zlib];
            packages = [wrappedPython];
          };
        });
  };
}
