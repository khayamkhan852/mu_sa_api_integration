# Salla API Integration

A Frappe custom application for seamless integration between Salla (Saudi Arabia's leading e-commerce platform) and ERPNext. This app enables automatic synchronization of products, customers, sales orders, and tax information from Salla stores to your ERPNext instance.

**Repository**: [https://github.com/khayamkhan852/mu_sa_api_integration](https://github.com/khayamkhan852/mu_sa_api_integration)

## Features

### 🔄 Data Synchronization
- **Products Sync**: Automatically sync products from Salla to ERPNext Items
  - Maps SKU, pricing, descriptions, categories, and availability
  - Creates Item Groups automatically
  - Handles product images and barcodes
  
- **Customers Sync**: Sync customer data from Salla to ERPNext
  - Automatically creates Customer Groups and Territories if missing
  - Maps customer contact information and addresses
  
- **Sales Orders Sync**: Import orders from Salla as Sales Orders in ERPNext
  - Prevents duplicate orders using Salla order IDs
  - Maps order items, quantities, and pricing
  - Sets transaction and delivery dates
  
- **Tax Sync**: Fetch and sync tax information from Salla

### 🏪 Multi-Shop Support
- Manage multiple Salla shops from a single ERPNext instance
- Each shop configuration stores its own API credentials
- Independent sync operations per shop

### ⏰ Automated Synchronization
- Hourly scheduled sync for all configured shops
- Background job processing for efficient data handling
- Error logging and reporting for failed syncs

## Requirements

- Frappe Framework (v14+)
- ERPNext (v14+)
- Python 3.10+
- Valid Salla API credentials (Bearer Token)

## Installation

### Using Bench

1. Navigate to your bench directory:
```bash
cd ~/frappe-bench
```

2. Install the app:
```bash
bench get-app https://github.com/khayamkhan852/mu_sa_api_integration.git
bench install-app mu_sa_api_integration
```

3. Migrate the database:
```bash
bench migrate
```

4. Restart bench:
```bash
bench restart
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/khayamkhan852/mu_sa_api_integration.git
```

2. Copy the app to your apps directory:
```bash
cp -r mu_sa_api_integration ~/frappe-bench/apps/
```

3. Install the app:
```bash
cd ~/frappe-bench
bench install-app mu_sa_api_integration
bench migrate
bench restart
```

## Usage

### Automatic Sync

The app automatically syncs data hourly for all configured shops. The sync process runs in the background and includes:
- Customer synchronization
- Product synchronization
- Sales Order synchronization

### Manual Sync

1. Navigate to **Shop** list in ERPNext
2. Select the shop you want to sync
3. Use the custom buttons in the list view or call the sync functions via console

## API Endpoints

The app uses the following Salla API endpoints:
- `https://api.salla.dev/admin/v2/products` - Products
- `https://api.salla.dev/admin/v2/customers` - Customers
- `https://api.salla.dev/admin/v2/orders` - Orders
- `https://api.salla.dev/admin/v2/taxes` - Taxes


## Scheduled Tasks

The app includes a scheduled task that runs hourly:
- **Function**: `mu_sa_api_integration.scheduler.sync_all_data_for_all_shops`
- **Frequency**: Hourly
- **Action**: Syncs customers, products, and sales orders for all configured shops

### Contributing

Contributions are welcome! Please follow these steps:

1. Fork the [repository](https://github.com/khayamkhan852/mu_sa_api_integration)
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions:
- **Email**: khayamkhan852@gmail.com
- **Publisher**: Khayam Khan

## Acknowledgments

- Built for Frappe Framework and ERPNext
- Integrates with Salla E-commerce Platform
- Uses Salla Admin API v2

**Note**: This app requires valid Salla API credentials. Make sure you have proper API access from your Salla merchant account before using this integration.
