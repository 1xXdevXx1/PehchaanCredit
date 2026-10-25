import os
import random
import argparse
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

SEED = 42

VENDORS_PROFILES = [
    ('Ramesh Tea & Snacks', 'Food & Beverage', 'Vellore', 'healthy'),
    ('Lakshmi Vegetable Stall', 'Fresh Produce', 'Katpadi', 'healthy'),
    ('Arun Mobile Repairs', 'Electronics Repair', 'Vellore', 'suspicious'),
    ('Priya Flower Mart', 'Florist', 'Vellore', 'seasonal'),
    ('Anand Grocery Store', 'Grocery Stall', 'Katpadi', 'growing'),
    ('Selvam Tailoring & Clothing', 'Clothing Vendor', 'Ranipet', 'irregular'),
    ('Murugan Idli Kadai', 'Street Snacks', 'Vellore', 'healthy'),
    ('Deepa Milk & Dairy', 'Dairy Vendor', 'Katpadi', 'healthy'),
    ('Karthik Fruit Juice Center', 'Food & Beverage', 'Vellore', 'growing'),
    ('Vijay Fast Food', 'Food & Beverage', 'Ranipet', 'low_volume'),
]

CITIES = ['Vellore', 'Katpadi', 'Ranipet', 'Walajah', 'Arcot']
BUSINESS_TYPES = [
    'Food & Beverage', 'Fresh Produce', 'Electronics Repair', 'Florist', 
    'Grocery Stall', 'Clothing Vendor', 'Street Snacks', 'Dairy Vendor'
]

INDIAN_FIRST_NAMES = [
    'Ramesh', 'Suresh', 'Lakshmi', 'Murugan', 'Kavitha', 'Arun', 'Priya', 
    'Anand', 'Selvam', 'Deepa', 'Karthik', 'Vijay', 'Venkatesh', 'Meena', 
    'Babu', 'Saravanan', 'Ganesh', 'Radha', 'Mani', 'Divya'
]
INDIAN_BIZ_SUFFIXES = [
    'Tea Stall', 'Vegetable Corner', 'Mobile Shop', 'Fruits & Juice', 
    'Provision Store', 'Boutique & Cloth', 'Tiffin Center', 'Milk Point', 
    'Sweet & Snacks', 'Flower Stall'
]

def generate_vendors(num_vendors=1000):
    np.random.seed(SEED)
    random.seed(SEED)
    
    vendors = []
    archetypes = ['healthy', 'growing', 'seasonal', 'irregular', 'low_volume', 'suspicious']
    archetype_weights = [0.40, 0.20, 0.15, 0.10, 0.08, 0.07]
    
    for i, (name, b_type, city, arch) in enumerate(VENDORS_PROFILES):
        v_id = f'VND-{1000 + i}'
        vendors.append({
            'vendor_id': v_id,
            'vendor_name': name,
            'business_type': b_type,
            'city': city,
            'vendor_age': random.randint(24, 60),
            'business_age_months': random.randint(12, 120),
            'archetype': arch
        })
        
    for i in range(len(VENDORS_PROFILES), num_vendors):
        v_id = f'VND-{1000 + i}'
        fname = random.choice(INDIAN_FIRST_NAMES)
        suffix = random.choice(INDIAN_BIZ_SUFFIXES)
        name = f'{fname} {suffix}'
        b_type = random.choice(BUSINESS_TYPES)
        city = random.choice(CITIES)
        arch = np.random.choice(archetypes, p=archetype_weights)
        vendors.append({
            'vendor_id': v_id,
            'vendor_name': name,
            'business_type': b_type,
            'city': city,
            'vendor_age': random.randint(21, 65),
            'business_age_months': random.randint(6, 180),
            'archetype': arch
        })
    return pd.DataFrame(vendors)

def generate_transactions(df_vendors, months=6):
    np.random.seed(SEED)
    random.seed(SEED)
    
    end_date = datetime(2026, 9, 2)
    start_date = end_date - timedelta(days=months * 30)
    
    tx_list = []
    tx_id_counter = 80000
    channels = ['UPI', 'CASH', 'WALLET', 'BANK_TRANSFER']
    
    # Pre-build circular rings among suspicious vendors
    suspicious_vendors = df_vendors[df_vendors['archetype'] == 'suspicious']['vendor_id'].tolist()
    circular_rings = []
    if len(suspicious_vendors) >= 3:
        for i in range(0, min(9, len(suspicious_vendors) - 2), 3):
            circular_rings.append((suspicious_vendors[i], suspicious_vendors[i+1], suspicious_vendors[i+2]))

    for _, vendor in df_vendors.iterrows():
        v_id = vendor['vendor_id']
        arch = vendor['archetype']
        b_type = vendor['business_type']
        city = vendor['city']
        
        # Determine number of transaction samples per vendor (realistic yet fast)
        n_samples = 120 if arch == 'healthy' else (100 if arch in ['growing', 'seasonal'] else 70)
        
        suppliers = [f'SUP-{v_id[-4:]}-{s}' for s in range(1, 4)]
        customers = [f'CUST-{random.randint(10000, 99999)}' for _ in range(25)]
        
        # Generate timestamps spread over months
        day_offsets = sorted(np.random.randint(0, months * 30, size=n_samples))
        
        for d_off in day_offsets:
            tx_id_counter += 1
            curr_time = start_date + timedelta(days=int(d_off))
            
            # Night heavy if suspicious
            if arch == 'suspicious' and random.random() < 0.28:
                h = random.choice([23, 0, 1, 2, 3, 4])
            else:
                h = random.randint(7, 21)
            curr_time = curr_time.replace(hour=h, minute=random.randint(0, 59), second=random.randint(0, 59))
            
            is_supp = (random.random() < 0.15) if arch != 'suspicious' else (random.random() < 0.04)
            if is_supp:
                t_type = 'SUPPLIER_PAYMENT'
                cparty = random.choice(suppliers)
                amt = round(random.uniform(2000, 8500), 2)
                ch = 'UPI' if random.random() < 0.7 else 'BANK_TRANSFER'
            else:
                t_type = 'CUSTOMER_PAYMENT'
                if arch == 'suspicious' and random.random() < 0.45:
                    cparty = customers[0] # concentrated
                    amt = float(random.choice([2500, 5000, 10000]))
                else:
                    cparty = random.choice(customers)
                    amt = round(random.uniform(50, 650), 2)
                ch = 'UPI' if random.random() < 0.85 else 'CASH'
                
            tx_list.append({
                'transaction_id': f'TXN-{tx_id_counter}',
                'timestamp': curr_time.strftime('%Y-%m-%d %H:%M:%S'),
                'vendor_id': v_id,
                'counterparty_id': cparty,
                'transaction_type': t_type,
                'amount': amt,
                'payment_channel': ch,
                'business_type': b_type,
                'city': city,
                'latitude': 12.9165 + random.uniform(-0.02, 0.02),
                'longitude': 79.1325 + random.uniform(-0.02, 0.02)
            })

    # Injected circular transactions
    for ring in circular_rings:
        vA, vB, vC = ring
        for c_idx in range(6):
            t_base = end_date - timedelta(days=c_idx * 15 + 2)
            amt = float(random.choice([15000, 25000]))
            for src, dst in [(vA, vB), (vB, vC), (vC, vA)]:
                tx_id_counter += 1
                t_base += timedelta(hours=2)
                tx_list.append({
                    'transaction_id': f'TXN-{tx_id_counter}',
                    'timestamp': t_base.strftime('%Y-%m-%d %H:%M:%S'),
                    'vendor_id': src,
                    'counterparty_id': dst,
                    'transaction_type': 'TRANSFER',
                    'amount': amt,
                    'payment_channel': 'UPI',
                    'business_type': 'Electronics Repair',
                    'city': 'Vellore',
                    'latitude': 12.9165,
                    'longitude': 79.1325
                })

    df_tx = pd.DataFrame(tx_list).sort_values('timestamp').reset_index(drop=True)
    return df_tx

def generate_repayment_labels(df_vendors, df_tx):
    np.random.seed(SEED)
    random.seed(SEED)
    labels = []
    vol_by_vendor = df_tx[df_tx['transaction_type'] == 'CUSTOMER_PAYMENT'].groupby('vendor_id')['amount'].sum().to_dict()
    
    for _, v in df_vendors.iterrows():
        v_id = v['vendor_id']
        arch = v['archetype']
        vol = vol_by_vendor.get(v_id, 10000)
        
        if arch == 'healthy': base_prob = 0.88 + random.uniform(-0.05, 0.05)
        elif arch == 'growing': base_prob = 0.84 + random.uniform(-0.05, 0.07)
        elif arch == 'seasonal': base_prob = 0.74 + random.uniform(-0.08, 0.08)
        elif arch == 'irregular': base_prob = 0.62 + random.uniform(-0.09, 0.09)
        elif arch == 'low_volume': base_prob = 0.58 + random.uniform(-0.10, 0.10)
        else: base_prob = 0.38 + random.uniform(-0.10, 0.10)
        
        prob = max(0.05, min(0.98, base_prob))
        default_flag = 1 if random.random() > prob else 0
        loan_amount = round(min(150000, max(15000, vol * 0.25)), -2)
        days_to_repay = random.randint(30, 180) if default_flag == 0 else random.randint(181, 360)
        
        labels.append({
            'vendor_id': v_id,
            'loan_id': f'LOAN-{v_id[-4:]}',
            'loan_amount': loan_amount,
            'repayment_probability': round(prob, 4),
            'default_flag': default_flag,
            'days_to_repay': days_to_repay
        })
    return pd.DataFrame(labels)

def main():
    parser = argparse.ArgumentParser(description='Generate reproducible synthetic vendor dataset.')
    parser.add_argument('--vendors', type=int, default=1000, help='Number of vendors to generate')
    parser.add_argument('--months', type=int, default=6, help='Months of transaction history')
    args = parser.parse_args()
    
    os.makedirs('data/synthetic', exist_ok=True)
    print(f'Generating {args.vendors} vendors...')
    df_v = generate_vendors(args.vendors)
    df_v.to_csv('data/synthetic/vendors.csv', index=False)
    
    print('Generating transactions...')
    df_tx = generate_transactions(df_v, args.months)
    df_tx.to_csv('data/synthetic/transactions.csv', index=False)
    
    print('Generating repayment labels...')
    df_labels = generate_repayment_labels(df_v, df_tx)
    df_labels.to_csv('data/synthetic/repayment_labels.csv', index=False)
    print(f'Done! Saved {len(df_v)} vendors, {len(df_tx)} transactions, {len(df_labels)} labels.')

if __name__ == '__main__':
    main()
