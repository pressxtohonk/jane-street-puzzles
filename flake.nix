{
  description = "Python notebook environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-24.11";
  };

  outputs = { self, nixpkgs }: 
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
    in 
    {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          venvDir = ".venv";
          packages = with pkgs; [ 
            python312 
            pyright
            ruff
          ] ++ (with pkgs.python312Packages; [
            pip
            ipykernel
            jupyter
            numpy
            ortools
            pandas
            plotly
            protobuf
            pydantic
            pytest
            seaborn
            scipy
            sympy
            matplotlib
            seaborn
            venvShellHook
          ]);
        };
      });
    };
}
