{
  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";
  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; config.allowUnfree = true; };
      });
    in
    {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python312
            aspell
            aspellDicts.en
            python312Packages.pyenchant
          ];
          
          shellHook = ''
            export ASPELL_CONF="dict-dir ${pkgs.aspellDicts.en}/lib/aspell"
            export ENCHANT_CONFIG_DIR="${pkgs.aspellDicts.en}/lib/aspell"
          '';
        };
      });
    };
}
