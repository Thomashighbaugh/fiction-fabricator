  # shell.nix
with import <nixpkgs> {};
mkShell {
 name = "python-devel";
 venvDir = "venv";
 
 buildInputs = with python311Packages; [ 
  openai
  cython
  fire
  retry
  ipython 
  ipython_genutils
  aiosqlite
  sqlitedict
  sqlite-utils
  venvShellHook
  python-dotenv
 ];

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc
    ]}
  '';



 postShellHook = ''source .venv/bin/activate; pip install -r requirements.txt''; }
