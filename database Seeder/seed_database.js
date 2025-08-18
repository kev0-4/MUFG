const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore, Timestamp } = require('firebase-admin/firestore');

// Initialize Firebase Admin SDK
const serviceAccount = require('./serviceAccountKey.json'); // Update with your service account key path
initializeApp({
  credential: cert(serviceAccount),
});
const db = getFirestore();

// Hardcoded data
const users = [
  { id: 'uid1', data: { name: 'John Doe', email: 'john.doe@example.com', createdAt: Timestamp.fromDate(new Date('2024-01-01')) } },
  { id: 'uid2', data: { name: 'Jane Smith', email: 'jane.smith@example.com', createdAt: Timestamp.fromDate(new Date('2024-02-01')) } },
  { id: 'uid3', data: { name: 'Alice Brown', email: 'alice.brown@example.com', createdAt: Timestamp.fromDate(new Date('2024-03-01')) } },
  { id: 'uid4', data: { name: 'Bob Johnson', email: 'bob.johnson@example.com', createdAt: Timestamp.fromDate(new Date('2024-04-01')) } },
  { id: 'uid5', data: { name: 'Emma Wilson', email: 'emma.wilson@example.com', createdAt: Timestamp.fromDate(new Date('2024-05-01')) } },
];

const portfolios = [
  { id: 'portfolio1', data: { userId: 'uid1', name: 'Superannuation', totalValue: 0, createdAt: Timestamp.fromDate(new Date('2024-01-01')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'portfolio2', data: { userId: 'uid2', name: 'Superannuation', totalValue: 0, createdAt: Timestamp.fromDate(new Date('2024-02-01')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'portfolio3', data: { userId: 'uid3', name: 'Superannuation', totalValue: 0, createdAt: Timestamp.fromDate(new Date('2024-03-01')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'portfolio4', data: { userId: 'uid4', name: 'Superannuation', totalValue: 0, createdAt: Timestamp.fromDate(new Date('2024-04-01')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'portfolio5', data: { userId: 'uid5', name: 'Superannuation', totalValue: 0, createdAt: Timestamp.fromDate(new Date('2024-05-01')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
];

const holdings = [
  // User 1
  { id: 'hold1', data: { userId: 'uid1', portfolioId: 'portfolio1', assetType: 'stock', symbol: 'BHP.AX', quantity: 100, purchasePrice: 25.00, currentPrice: 27.50, purchaseDate: Timestamp.fromDate(new Date('2024-06-01')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold2', data: { userId: 'uid1', portfolioId: 'portfolio1', assetType: 'bond', symbol: 'AU10Y', quantity: 50, purchasePrice: 100.00, currentPrice: 99.00, purchaseDate: Timestamp.fromDate(new Date('2024-07-01')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold3', data: { userId: 'uid1', portfolioId: 'portfolio1', assetType: 'etf', symbol: 'VAS.AX', quantity: 80, purchasePrice: 50.00, currentPrice: 52.00, purchaseDate: Timestamp.fromDate(new Date('2024-08-01')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  // User 2
  { id: 'hold4', data: { userId: 'uid2', portfolioId: 'portfolio2', assetType: 'stock', symbol: 'CBA.AX', quantity: 120, purchasePrice: 80.00, currentPrice: 85.00, purchaseDate: Timestamp.fromDate(new Date('2024-06-15')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold5', data: { userId: 'uid2', portfolioId: 'portfolio2', assetType: 'bond', symbol: 'AU5Y', quantity: 60, purchasePrice: 95.00, currentPrice: 94.50, purchaseDate: Timestamp.fromDate(new Date('2024-07-15')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold6', data: { userId: 'uid2', portfolioId: 'portfolio2', assetType: 'etf', symbol: 'VGS.AX', quantity: 70, purchasePrice: 60.00, currentPrice: 62.00, purchaseDate: Timestamp.fromDate(new Date('2024-08-15')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  // User 3
  { id: 'hold7', data: { userId: 'uid3', portfolioId: 'portfolio3', assetType: 'stock', symbol: 'WBC.AX', quantity: 90, purchasePrice: 30.00, currentPrice: 32.00, purchaseDate: Timestamp.fromDate(new Date('2024-06-20')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold8', data: { userId: 'uid3', portfolioId: 'portfolio3', assetType: 'bond', symbol: 'AU10Y', quantity: 40, purchasePrice: 98.00, currentPrice: 97.50, purchaseDate: Timestamp.fromDate(new Date('2024-07-20')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold9', data: { userId: 'uid3', portfolioId: 'portfolio3', assetType: 'etf', symbol: 'VAS.AX', quantity: 100, purchasePrice: 48.00, currentPrice: 50.00, purchaseDate: Timestamp.fromDate(new Date('2024-08-20')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  // User 4
  { id: 'hold10', data: { userId: 'uid4', portfolioId: 'portfolio4', assetType: 'stock', symbol: 'ANZ.AX', quantity: 110, purchasePrice: 28.00, currentPrice: 29.50, purchaseDate: Timestamp.fromDate(new Date('2024-06-25')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold11', data: { userId: 'uid4', portfolioId: 'portfolio4', assetType: 'bond', symbol: 'AU2Y', quantity: 55, purchasePrice: 99.00, currentPrice: 98.50, purchaseDate: Timestamp.fromDate(new Date('2024-07-25')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold12', data: { userId: 'uid4', portfolioId: 'portfolio4', assetType: 'etf', symbol: 'VTS.AX', quantity: 85, purchasePrice: 55.00, currentPrice: 57.00, purchaseDate: Timestamp.fromDate(new Date('2024-08-25')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  // User 5
  { id: 'hold13', data: { userId: 'uid5', portfolioId: 'portfolio5', assetType: 'stock', symbol: 'MQG.AX', quantity: 95, purchasePrice: 90.00, currentPrice: 92.00, purchaseDate: Timestamp.fromDate(new Date('2024-06-30')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold14', data: { userId: 'uid5', portfolioId: 'portfolio5', assetType: 'bond', symbol: 'AU10Y', quantity: 45, purchasePrice: 97.00, currentPrice: 96.50, purchaseDate: Timestamp.fromDate(new Date('2024-07-30')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
  { id: 'hold15', data: { userId: 'uid5', portfolioId: 'portfolio5', assetType: 'etf', symbol: 'VAS.AX', quantity: 90, purchasePrice: 49.00, currentPrice: 51.00, purchaseDate: Timestamp.fromDate(new Date('2024-08-30')), updatedAt: Timestamp.fromDate(new Date('2025-08-18')) } },
];

const categories = [
  // User 1
  { id: 'cat1', data: { userId: 'uid1', name: 'Salary', type: 'income' } },
  { id: 'cat2', data: { userId: 'uid1', name: 'Groceries', type: 'expense' } },
  { id: 'cat3', data: { userId: 'uid1', name: 'Utilities', type: 'expense' } },
  // User 2
  { id: 'cat4', data: { userId: 'uid2', name: 'Salary', type: 'income' } },
  { id: 'cat5', data: { userId: 'uid2', name: 'Groceries', type: 'expense' } },
  { id: 'cat6', data: { userId: 'uid2', name: 'Utilities', type: 'expense' } },
  // User 3
  { id: 'cat7', data: { userId: 'uid3', name: 'Salary', type: 'income' } },
  { id: 'cat8', data: { userId: 'uid3', name: 'Groceries', type: 'expense' } },
  { id: 'cat9', data: { userId: 'uid3', name: 'Utilities', type: 'expense' } },
  // User 4
  { id: 'cat10', data: { userId: 'uid4', name: 'Salary', type: 'income' } },
  { id: 'cat11', data: { userId: 'uid4', name: 'Groceries', type: 'expense' } },
  { id: 'cat12', data: { userId: 'uid4', name: 'Utilities', type: 'expense' } },
  // User 5
  { id: 'cat13', data: { userId: 'uid5', name: 'Salary', type: 'income' } },
  { id: 'cat14', data: { userId: 'uid5', name: 'Groceries', type: 'expense' } },
  { id: 'cat15', data: { userId: 'uid5', name: 'Utilities', type: 'expense' } },
];

const transactions = [
  // User 1
  { id: 'tx1', data: { userId: 'uid1', amount: 2000.00, categoryId: 'cat1', date: Timestamp.fromDate(new Date('2024-08-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx2', data: { userId: 'uid1', amount: 150.00, categoryId: 'cat2', date: Timestamp.fromDate(new Date('2024-08-02')), description: 'Grocery shopping', type: 'expense' } },
  { id: 'tx3', data: { userId: 'uid1', amount: 100.00, categoryId: 'cat3', date: Timestamp.fromDate(new Date('2024-08-03')), description: 'Electricity bill', type: 'expense' } },
  { id: 'tx4', data: { userId: 'uid1', amount: 2500.00, categoryId: 'cat1', date: Timestamp.fromDate(new Date('2024-09-01')), description: 'Bonus payment', type: 'income' } },
  { id: 'tx5', data: { userId: 'uid1', amount: 200.00, categoryId: 'cat2', date: Timestamp.fromDate(new Date('2024-09-02')), description: 'Supermarket', type: 'expense' } },
  // User 2
  { id: 'tx6', data: { userId: 'uid2', amount: 2200.00, categoryId: 'cat4', date: Timestamp.fromDate(new Date('2024-08-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx7', data: { userId: 'uid2', amount: 120.00, categoryId: 'cat5', date: Timestamp.fromDate(new Date('2024-08-02')), description: 'Grocery shopping', type: 'expense' } },
  { id: 'tx8', data: { userId: 'uid2', amount: 90.00, categoryId: 'cat6', date: Timestamp.fromDate(new Date('2024-08-03')), description: 'Water bill', type: 'expense' } },
  { id: 'tx9', data: { userId: 'uid2', amount: 1800.00, categoryId: 'cat4', date: Timestamp.fromDate(new Date('2024-09-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx10', data: { userId: 'uid2', amount: 140.00, categoryId: 'cat5', date: Timestamp.fromDate(new Date('2024-09-02')), description: 'Supermarket', type: 'expense' } },
  // User 3
  { id: 'tx11', data: { userId: 'uid3', amount: 1900.00, categoryId: 'cat7', date: Timestamp.fromDate(new Date('2024-08-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx12', data: { userId: 'uid3', amount: 160.00, categoryId: 'cat8', date: Timestamp.fromDate(new Date('2024-08-02')), description: 'Grocery shopping', type: 'expense' } },
  { id: 'tx13', data: { userId: 'uid3', amount: 110.00, categoryId: 'cat9', date: Timestamp.fromDate(new Date('2024-08-03')), description: 'Internet bill', type: 'expense' } },
  { id: 'tx14', data: { userId: 'uid3', amount: 2000.00, categoryId: 'cat7', date: Timestamp.fromDate(new Date('2024-09-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx15', data: { userId: 'uid3', amount: 130.00, categoryId: 'cat8', date: Timestamp.fromDate(new Date('2024-09-02')), description: 'Supermarket', type: 'expense' } },
  // User 4
  { id: 'tx16', data: { userId: 'uid4', amount: 2100.00, categoryId: 'cat10', date: Timestamp.fromDate(new Date('2024-08-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx17', data: { userId: 'uid4', amount: 170.00, categoryId: 'cat11', date: Timestamp.fromDate(new Date('2024-08-02')), description: 'Grocery shopping', type: 'expense' } },
  { id: 'tx18', data: { userId: 'uid4', amount: 120.00, categoryId: 'cat12', date: Timestamp.fromDate(new Date('2024-08-03')), description: 'Gas bill', type: 'expense' } },
  { id: 'tx19', data: { userId: 'uid4', amount: 2300.00, categoryId: 'cat10', date: Timestamp.fromDate(new Date('2024-09-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx20', data: { userId: 'uid4', amount: 180.00, categoryId: 'cat11', date: Timestamp.fromDate(new Date('2024-09-02')), description: 'Supermarket', type: 'expense' } },
  // User 5
  { id: 'tx21', data: { userId: 'uid5', amount: 2400.00, categoryId: 'cat13', date: Timestamp.fromDate(new Date('2024-08-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx22', data: { userId: 'uid5', amount: 140.00, categoryId: 'cat14', date: Timestamp.fromDate(new Date('2024-08-02')), description: 'Grocery shopping', type: 'expense' } },
  { id: 'tx23', data: { userId: 'uid5', amount: 130.00, categoryId: 'cat15', date: Timestamp.fromDate(new Date('2024-08-03')), description: 'Electricity bill', type: 'expense' } },
  { id: 'tx24', data: { userId: 'uid5', amount: 2600.00, categoryId: 'cat13', date: Timestamp.fromDate(new Date('2024-09-01')), description: 'Monthly salary', type: 'income' } },
  { id: 'tx25', data: { userId: 'uid5', amount: 190.00, categoryId: 'cat14', date: Timestamp.fromDate(new Date('2024-09-02')), description: 'Supermarket', type: 'expense' } },
];

// Calculate portfolio totalValue
portfolios.forEach(portfolio => {
  const portfolioHoldings = holdings.filter(h => h.data.portfolioId === portfolio.id);
  portfolio.data.totalValue = portfolioHoldings.reduce(
    (sum, h) => sum + h.data.quantity * h.data.currentPrice,
    0
  );
});

// Main seeding function
async function seedFirestore() {
  console.log('Starting Firestore seeding...');
  let userCount = 0, portfolioCount = 0, holdingCount = 0, categoryCount = 0, transactionCount = 0;

  // Batch write
  const batch = db.batch();

  // Seed users
  users.forEach(user => {
    batch.set(db.collection('users').doc(user.id), user.data);
  });
  userCount = users.length;

  // Seed portfolios
  portfolios.forEach(portfolio => {
    batch.set(db.collection('portfolios').doc(portfolio.id), portfolio.data);
  });
  portfolioCount = portfolios.length;

  // Seed holdings
  holdings.forEach(holding => {
    batch.set(db.collection('holdings').doc(holding.id), holding.data);
  });
  holdingCount = holdings.length;

  // Seed categories
  categories.forEach(category => {
    batch.set(db.collection('categories').doc(category.id), category.data);
  });
  categoryCount = categories.length;

  // Seed transactions
  transactions.forEach(transaction => {
    batch.set(db.collection('transactions').doc(transaction.id), transaction.data);
  });
  transactionCount = transactions.length;

  // Commit batch
  await batch.commit();

  console.log(`Seeding complete!`);
  console.log(`Users: ${userCount}`);
  console.log(`Portfolios: ${portfolioCount}`);
  console.log(`Holdings: ${holdingCount}`);
  console.log(`Categories: ${categoryCount}`);
  console.log(`Transactions: ${transactionCount}`);
}

// Error handling and execution
seedFirestore()
  .then(() => console.log('Firestore seeding successful!'))
  .catch(error => {
    console.error('Error seeding Firestore:', error);
    process.exit(1);
  });