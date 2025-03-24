import streamlit as st
import json
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from io import BytesIO

# .env の読み込み
load_dotenv()

KEY = os.getenv("AZURE_KEY")
ENDPOINT = os.getenv("AZURE_ENDPOINT")

# Azureクライアント初期化
credential = AzureKeyCredential(KEY)
document_intelligence_client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=credential)

# Streamlitインターフェース
st.title("Azure AI Document Intelligence [OCR demo]")

# 対応するファイル形式
supported_file_types = ["pdf", "jpeg", "jpg", "png", "bmp", "tiff", "heif", "docx", "xlsx", "pptx", "html"]

uploaded_file = st.file_uploader("ファイルをアップロードしてください", type=supported_file_types)

if uploaded_file is not None:
    # 解析ボタン
    if st.button("解析開始"):
        with st.spinner("解析中..."):
            try:
                # ファイル拡張子の取得
                file_extension = uploaded_file.name.split(".")[-1].lower()

                # ファイルをバイナリとして読み込み
                file_content = uploaded_file.read()

                # 解析の実行
                poller = document_intelligence_client.begin_analyze_document(
                    model_id="prebuilt-layout",
                    body=file_content
                )
                result = poller.result()

                # 解析結果の取得
                analyze_result = result.as_dict()

                # 解析結果をJSONとして作成
                output_data = {
                    "status": poller.status(),
                    "createdDateTime": poller.details.get("createdDateTime", ""),
                    "lastUpdatedDateTime": poller.details.get("lastUpdatedDateTime", ""),
                    "analyzeResult": analyze_result
                }

                # JSONファイルをダウンロードできるようにする
                json_file = BytesIO()
                json_file.write(json.dumps(output_data, indent=4, ensure_ascii=False).encode('utf-8'))
                json_file.seek(0)

                st.download_button(
                    label="結果をダウンロード (JSON)",
                    data=json_file,
                    file_name="result.json",
                    mime="application/json"
                )

                # 結果を画面に表示
                st.json(output_data)

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
