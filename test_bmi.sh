sleep 5
if curl "api:3000/?height=174&weight=88" | grep -q 'Overweight'; then
  echo "Tests passed!"
  exit 0
else
  echo "Tests failed!"
  exit 1
fi