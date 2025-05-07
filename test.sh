# Show containers healthy
curl -s localhost:8081/health && echo      # → {"status":"ok"}
curl -s localhost:8082/health && echo      # → {"status":"ok"}

# Happy path
CID=$(curl -s -X POST localhost:8081/customers \
      -H 'Content-Type: application/json' \
      -d '{"first_name":"John","last_name":"Smith","dob":"1989-02-17","smoker":false}' | jq .customerId)

curl -s -X POST localhost:8082/underwrite \
     -H 'Content-Type: application/json' \
     -d "{\"customerId\":$CID,\"coverage\":100000}" | jq .
# Output
# {
#   "customerId": 1,
#   "decision": "APPROVED",
#   "annualPremium": 300.0
# }

# Decline path (age too high)
CID2=$(curl -s -X POST localhost:8081/customers \
      -H 'Content-Type: application/json' \
      -d '{"first_name":"Bob","last_name":"Elder","dob":"1940-04-01","smoker":false}' | jq .customerId)

curl -s -X POST localhost:8082/underwrite \
     -H 'Content-Type: application/json' \
     -d "{\"customerId\":$CID2,\"coverage\":100000}" | jq .
# decision = "DECLINED"


#### Duplicate policy test ####
# First policy (works)
curl -X POST localhost:8083/policies \
     -H 'Content-Type: application/json' \
     -d '{"customerId":42,"coverage":100000,"annualPremium":300.0}'

# Duplicate policy (409)
curl -X POST localhost:8083/policies \
     -H 'Content-Type: application/json' \
     -d '{"customerId":42,"coverage":150000,"annualPremium":450.0}'
# → HTTP/1.1 409 Conflict
# {"detail":"Customer 42 already has a policy"}