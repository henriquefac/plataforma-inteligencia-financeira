import pandas as pd
from app.domain.data_artifact import DataArtifact
from app.core.config import settingsInst
from .util import SCHEMA


class PreProcessService:

    def __init__(self):
        self.df = None
        self.df_validos = None
        self.df_invalidos = None
        self.log = {}

    # -------------------------
    def _init_state(self, df: pd.DataFrame):
        self.df = df.copy()
        self.log = {
            "linhas_iniciais": len(df),
            "etapas": {}
        }

    # -------------------------
    def see_if_null(self):
        total = len(self.df)

        nulos = self.df.isnull().sum()
        percentual = (nulos / total) * 100

        self.log["etapas"]["nulos"] = {
            col: {
                "nulos": int(nulos[col]),
                "percentual": float(percentual[col])
            }
            for col in self.df.columns
        }

    # -------------------------
    def check_if_all_columns(self):
        log = {}

        for col in settingsInst.COLUNAS:
            log[col] = col in self.df.columns

        self.log["etapas"]["estrutura"] = log

        if not all(log.values()):
            missing = [col for col, ok in log.items() if not ok]
            raise ValueError(
                f"Tabela incompleta, faltando: {', '.join(missing)}"
            )

    # -------------------------
    def normalize_text(self):
        alterations = 0

        for col in self.df.columns:
            if (
                pd.api.types.is_string_dtype(self.df[col]) or
                self.df[col].dtype == "object"
            ):
                before = self.df[col].copy()

                self.df[col] = (
                    self.df[col]
                    .astype("string")
                    .str.strip()
                    .str.lower()
                )

                alterations += (before != self.df[col]).sum()

        self.log["etapas"]["text"] = {
            "valores_alterados": int(alterations)
        }

    # -------------------------
    def apply_schema(self):
        log_tipo = {}

        for col, func in SCHEMA.items():
            if col not in self.df.columns:
                continue

            before = self.df[col].isnull().sum()

            self.df[col] = func(self.df[col])

            after = self.df[col].isnull().sum()

            log_tipo[col] = {
                "nulos_antes": int(before),
                "nulos_depois": int(after),
                "diferenca": int(after - before)
            }

        self.log["etapas"]["schema"] = log_tipo

    # -------------------------
    def validate_status(self):
        if "status" not in self.df.columns:
            return None

        mask_invalid = ~self.df["status"].isin(settingsInst.STATUS_VALIDOS)

        invalid_val = self.df.loc[mask_invalid, "status"].unique()

        self.log["etapas"]["status"] = {
            "quantidade_invalidos": int(mask_invalid.sum()),
            "valores_invalidos": list(invalid_val)
        }

        return mask_invalid

    # -------------------------
    def split_status(self, mask_invalidos):
        if mask_invalidos is None:
            self.df_validos = self.df.copy()
            self.df_invalidos = pd.DataFrame()
            return

        self.df_validos = self.df[~mask_invalidos]
        self.df_invalidos = self.df[mask_invalidos]

    # -------------------------
    def run(self, data: DataArtifact) -> dict:
        try:
            # 1. carregar dados
            df = data.load_raw()

            # 2. init estado
            self._init_state(df)

            # 3. valida estrutura
            self.check_if_all_columns()

            # 4. processamento
            self.normalize_text()
            self.apply_schema()

            mask_invalidos = self.validate_status()
            self.split_status(mask_invalidos)

            self.see_if_null()

            self.log["linhas_finais"] = len(self.df)

            # 5. salvar resultado
            data.save_processed(self.df)

            return {
                "status": data.status,
                "linhas": len(self.df),
                "invalidos": len(self.df_invalidos),
                "log": self.log
            }

        except Exception as e:
            data.status = "error"
            data._save_metadata()
            raise e