import numexpr as ne
import streamlit as st
from datetime import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from functions.clutch_prediction.create_features import create_feature_table_class
from utils.expanding_filter import ExpandingVisFilterAI

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, classification_report
from sklearn.model_selection import GridSearchCV, train_test_split

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import silhouette_score, auc, roc_curve

st.title("AI module - clutch situation prediction with classification")


filterer = ExpandingVisFilterAI()

if st.button("Perform Classification"):
    df = create_feature_table_class(filterer.feed_match_idx())
    unnecessary_columns = ["match_name", "clutch_team", "tick_num"]

    df = df[list((set(df.columns) - set(unnecessary_columns)))]
    df.replace({True: 1, False: 0}, inplace=True)
    df.replace({"N/A": 0}, inplace=True)
    good_maps = ['de_overpass', 'de_nuke', 'de_ancient', 'de_dust2', 'de_inferno', 'de_anubis',
        'de_mirage', 'de_vertigo']

    good_alive_enemies = [2,3,4,5]

    df = df[df['map_name'].isin(good_maps)]
    df = df[df['alive_enemies'].isin(good_alive_enemies)]
    df = df[df['enemy_health_total']<=500]
    encoded_df = pd.get_dummies(df, columns=['map_name','player_side'])
    encoded_df = encoded_df.fillna(0)
    target = ['clutch_won']
    features = [col for col in encoded_df.columns if col not in target]

    # Same standardization must be applied to test
    scaler = StandardScaler()
    encoded_df[features] = scaler.fit_transform(encoded_df[features])

    X = encoded_df[features]  # Assuming 'target_column' is the name of your target column
    y = encoded_df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42,stratify=y)
    rndf = RandomForestClassifier(n_estimators=35, max_depth=8, max_features=7, random_state=107, min_samples_split=30, min_samples_leaf=4, criterion='log_loss', bootstrap=True, n_jobs = -1, class_weight='balanced_subsample')
    rndf.fit(X_train, np.ravel(y_train))

    with st.expander("Confusion Matrix"):
        st.write(confusion_matrix(y_test, rndf.predict(X_test)))

    # with st.expander("ROC Curve"):
    #     # Calculate FPR, TPR and AUC
    #     probs = rndf.predict_proba(X_test)
    #     preds = probs[:, 1]
    #     fpr, tpr, threshold = roc_curve(X_test, preds)
    #     roc_auc = auc(fpr, tpr)

    #     # Plot ROC Curve
    #     fig, ax = plt.subplots()
    #     ax.set_title('ROC Curve (Validation set)')
    #     ax.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
    #     ax.plot([0, 1], [0, 1], 'r--')
    #     ax.set_xlim([0, 1])
    #     ax.set_ylim([0, 1])
    #     ax.set_ylabel('True Positive Rate')
    #     ax.set_xlabel('False Positive Rate')
    #     ax.legend(loc='lower right')

    #     st.pyplot(fig)

    with st.expander("Feature Importance"):
        imp_features = rndf.feature_importances_
        df_imp_features = pd.DataFrame({"features": features, "weights": imp_features})
        df_imp_features = df_imp_features.sort_values(by='weights', ascending=True).tail(10)  # for horizontal bar plot

        # Create the plot
        fig, ax = plt.subplots()
        df_imp_features.set_index('features').plot.barh(ax=ax, legend=False)
        ax.set_title("Top 10 Feature Importances")
        ax.set_xlabel("Importance Weight")
        ax.set_ylabel("Features")
        st.pyplot(fig)

    y_pred = pd.DataFrame(rndf.predict(X), columns = ['pred'])
    st.write(df.merge(y_pred,how='left', validate='1:1', left_index=True, right_index=True))
