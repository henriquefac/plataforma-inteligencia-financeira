import pandas as pd
from .config import (SCHEMA, COLUNAS, 
    STATUS_VALIDOS, RestultPreProcess)

class PreProcess:
    def __init__(self, df: pd.DataFrame):
        # self.df_raw = df.copy()
        self.df = df.copy()

        self.log = {
            "linhas_iniciais": len(df),
            "etapas": {}
        }

    def see_if_null(self):
        total = len(self.df)

        nulos = self.df.isnull().sum()
        percentual = (nulos / total) * 100

        resultado = pd.DataFrame({
            "nulos": nulos,
            "percentual (%)": percentual
        })

        self.log["etapas"]["nulos"] = resultado.to_dict()

        return resultado
    
    # checar se a tabela possui as tabelas obrigatórias
    def check_if_all_colunms(self):
        log = {}
        for col in COLUNAS:
            if col in self.df.columns:
                log[col] = True
            else:
                log[col] = False


    def normalize_text(self):
        # contagens das alterações feitas. Número de intens alterados total, por cálula
        alterations = 0

        for col in self.df.columns:
            if (pd.api.types.is_string_dtype(self.df[col]) or 
            self.df[col].dtype == "object"): # Verifica se a coluna pode ser uma string
                
                before = self.df[col].copy()

                self.df[col] = (
                    self.df[col]
                    .astype("string")
                    .str.strip()
                    .str.lower()
                )
                
                alterations += (before != self.df[col]).sum()
        self.log["etapas"]["text"] = {
            "valores_alterados" : int(alterations)
        }

    def apply_schema(self):
        # apara cada coluna, tem uma função específica
        # para garantir a tipagem correta de cada um dos valores
        # das colunas
        log_tipo = {}

        for col, func in SCHEMA.items():
            if col not in self.df.columns:
                continue 
            # Antes de aplicar as funções de cada co
            before = self.df[col].isnull().sum()

            self.df[col] = func(self.df[col])

            after = self.df[col].isnull().sum()

            log_tipo[col] = {
                "nulos_antes": int(before),
                "nulos_depois": int(after),
                "introduzidos": int(before - after)
            }
        self.log["etapas"]["schema"] = log_tipo
    
    def validate_status(self):
        if "status" not in self.df.columns:
            return None

        mask_invalid = ~self.df["status"].isin(STATUS_VALIDOS)

        invalid_val = self.df.loc[mask_invalid, "status"].unique()

        self.log["etapas"]["status"] = {
            "quantidade_invalidos": int(mask_invalid.sum()),
            "valores_invalidos": list(invalid_val)
        }

        return mask_invalid

    def split_status(self, mask_invalidos):
        if mask_invalidos is None:
            self.df_validos = self.df.copy()
            self.df_invalidos = pd.DataFrame()
            return

        self.df_validos = self.df[~mask_invalidos]
        self.df_invalidos = self.df[mask_invalidos]

    def run(self):
        self.normalize_text()
        self.apply_schema()

        mask_invalidos = self.validate_status()
        self.split_status(mask_invalidos)

        self.see_if_null()

        self.log["linhas_finais"] = len(self.df)

        return RestultPreProcess(self.df, self.df_validos, 
                                 self.df_invalidos, self.log)