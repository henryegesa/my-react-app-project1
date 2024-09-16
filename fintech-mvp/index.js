const express = require('express');
const app = express();

app.get('/', (req, res) => res.send('Hello, world-mzuri!'));

app.listen(3000, () => console.log('Server is running on http://localhost:3000'));

const stripe = require('stripe')('your-stripe-secret-key');

app.post('/payment', async (req, res) => {
  const paymentIntent = await stripe.paymentIntents.create({
    amount: 2000, // amount in cents
    currency: 'usd',
    payment_method_types: ['card'],
  });
  res.send(paymentIntent);
});
