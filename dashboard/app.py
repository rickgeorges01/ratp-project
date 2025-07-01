#!/usr/bin/env python3
"""
Dashboard Test Simple - Streamlit
"""
import streamlit as st
import pandas as pd
import time
import json
import os
from kafka import KafkaConsumer
import plotly.express as px

st.set_page_config(
    page_title="RATP Test Dashboard",
    layout="wide"
)

st.title("RATP Observatoire - Test Dashboard")


# Test connexions
@st.cache_resource
def test_connections():
    results = {}

    # Test Kafka
    try:
        servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
        consumer = KafkaConsumer(
            'pm10-data',
            bootstrap_servers=[servers],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        results['kafka'] = "Connecté"
        consumer.close()
    except Exception as e:
        results['kafka'] = f"Erreur: {str(e)[:50]}"

    # Test MinIO
    try:
        import boto3
        minio_endpoint = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
        s3 = boto3.client(
            's3',
            endpoint_url=minio_endpoint,
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin123'
        )
        s3.list_buckets()
        results['minio'] = "Connecté"
    except Exception as e:
        results['minio'] = f"Erreur: {str(e)[:50]}"

    return results


# Interface
col1, col2 = st.columns(2)

with col1:
    st.subheader("Test Connexions")

    if st.button("Tester Connexions"):
        with st.spinner("Test en cours..."):
            results = test_connections()

        for service, status in results.items():
            st.write(f"**{service.upper()}:** {status}")

with col2:
    st.subheader("Données Simulées")

    # Graphique test avec données simulées
    if st.button("Générer Graphique Test"):
        dates = pd.date_range('2024-01-01', periods=100, freq='H')
        pm10_data = [50 + i % 30 for i in range(100)]

        df_test = pd.DataFrame({
            'timestamp': dates,
            'pm10': pm10_data
        })

        fig = px.line(df_test, x='timestamp', y='pm10',
                      title='PM10 - Données Test')
        st.plotly_chart(fig, use_container_width=True)

# Section logs temps réel
st.subheader("📡 Messages Kafka (Test)")

# Placeholder pour messages
msg_placeholder = st.empty()

# Auto-refresh simulé
if st.checkbox("Auto-refresh (30s)"):
    while True:
        current_time = time.strftime("%H:%M:%S")
        test_msg = f"[{current_time}] Message test - Station: Auber, PM10: {50 + int(time.time()) % 20}"

        msg_placeholder.text(test_msg)
        time.sleep(30)

st.sidebar.info("Dashboard Test - Vérification connexions infrastructure")