{
  description = "GEP development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          inherit (pkgs) lib stdenv;
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              fzf
              gnumake
              shellcheck
              shfmt
              uv
              tmux
              gdb
              zig_0_16
            ];

            shellHook = ''
              echo "GEP development shell"
              echo "  setup: uv sync --group dev"
              echo "  lint:  ./lint.sh"
              echo "  test:  ./tests.sh"
              echo "  run:   gdb -q -ex 'source ./gdbinit-gep.py'"
            '';
          };
        }
      );
    };
}
