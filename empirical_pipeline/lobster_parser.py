import pandas as pd
import numpy as np
import os
import glob

class LOBSTERParser:
    def __init__(self, data_dir, levels=10):
        self.data_dir = data_dir
        self.levels = levels
        
    def load_day_data(self, ticker):
        """Finds and loads the message and orderbook files for a given ticker."""
        msg_files = glob.glob(os.path.join(self.data_dir, f"{ticker}_*message*.csv"))
        ob_files = glob.glob(os.path.join(self.data_dir, f"{ticker}_*orderbook*.csv"))
        
        if not msg_files or not ob_files:
            raise FileNotFoundError(f"Could not find LOBSTER data for {ticker} in {self.data_dir}")
            
        msg_file = sorted(msg_files)[0]
        ob_file = sorted(ob_files)[0]
        
        print(f"Loading Message File: {os.path.basename(msg_file)}")
        print(f"Loading Orderbook File: {os.path.basename(ob_file)}")
        
        # Message columns: Time, Type, OrderID, Size, Price, Direction
        msg_cols = ['Time', 'Type', 'OrderID', 'Size', 'Price', 'Direction']
        df_msg = pd.read_csv(msg_file, names=msg_cols)
        
        # Orderbook columns: AskPrice1, AskSize1, BidPrice1, BidSize1, ...
        ob_cols = []
        for i in range(1, self.levels + 1):
            ob_cols.extend([f'AskPrice_{i}', f'AskSize_{i}', f'BidPrice_{i}', f'BidSize_{i}'])
            
        df_ob = pd.read_csv(ob_file, names=ob_cols)
        
        # Merge on index (LOBSTER files are strictly row-aligned)
        df = pd.concat([df_msg, df_ob], axis=1)
        
        # Convert prices (LOBSTER prices are in ten-thousandths of a cent, i.e., / 10000)
        price_cols = [c for c in df.columns if 'Price' in c]
        for col in price_cols:
            df[col] = df[col] / 10000.0
            
        return df

    def extract_microstructure_features(self, df):
        """Calculates mid-price, spread, and order flow imbalance (OFI)."""
        df['MidPrice'] = (df['AskPrice_1'] + df['BidPrice_1']) / 2.0
        df['Spread'] = df['AskPrice_1'] - df['BidPrice_1']
        
        # Calculate Order Flow Imbalance (OFI) as a proxy for algorithmic pressure
        # OFI = change in bid size (if bid price >= prev bid) - change in ask size (if ask <= prev ask)
        # Simplified volume imbalance for this skeleton:
        df['VolumeImbalance'] = df['BidSize_1'] - df['AskSize_1']
        
        return df

if __name__ == "__main__":
    print("LOBSTER Parser Initialized. Waiting for data...")
    # parser = LOBSTERParser('empirical_pipeline/data')
    # df = parser.load_day_data('AMZN')
    # df = parser.extract_microstructure_features(df)
    # print(df.head())
