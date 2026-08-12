/**
 * Integration Test - Frontend to Backend API
 * Tests the ticket verification endpoint
 */

const API_URL = "http://localhost:8000";

async function testTicketVerification(ticketId, expectSuccess) {
  console.log(`\n${"=".repeat(70)}`);
  console.log(`Testing: ${ticketId}`);
  console.log(`Expected: ${expectSuccess ? "SUCCESS" : "FAILURE"}`);
  console.log("=".repeat(70));

  try {
    const response = await fetch(`${API_URL}/api/ticket/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticket_id: ticketId }),
    });

    console.log(`Status: ${response.status} ${response.statusText}`);

    if (response.ok) {
      const data = await response.json();
      console.log("\nResponse Data:");
      console.log(JSON.stringify(data, null, 2));

      if (expectSuccess) {
        console.log("\n✅ TEST PASSED - Valid ticket verified successfully");
        console.log(`   Session ID: ${data.session_id}`);
        console.log(`   Gate: ${data.gate}`);
        console.log(`   Block: ${data.block}`);
        console.log(`   Seat: ${data.seat}`);
        console.log(`   Parking: ${data.parking}`);
        return true;
      } else {
        console.log("\n❌ TEST FAILED - Expected failure but got success");
        return false;
      }
    } else {
      const errorData = await response.json();
      console.log("\nError Response:");
      console.log(JSON.stringify(errorData, null, 2));

      if (!expectSuccess && response.status === 404) {
        console.log("\n✅ TEST PASSED - Invalid ticket rejected as expected");
        return true;
      } else {
        console.log("\n❌ TEST FAILED - Unexpected error response");
        return false;
      }
    }
  } catch (error) {
    console.log(`\n❌ TEST FAILED - Network error: ${error.message}`);
    return false;
  }
}

async function runTests() {
  console.log("\n" + "=".repeat(70));
  console.log("CROWDSHIELD AI - FRONTEND → BACKEND INTEGRATION TESTS");
  console.log("=".repeat(70));

  let passed = 0;
  let failed = 0;

  // Test 1: Valid ticket T0004
  if (await testTicketVerification("T0004", true)) {
    passed++;
  } else {
    failed++;
  }

  // Test 2: Invalid ticket
  if (await testTicketVerification("INVALID123", false)) {
    passed++;
  } else {
    failed++;
  }

  console.log("\n" + "=".repeat(70));
  console.log("TEST SUMMARY");
  console.log("=".repeat(70));
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Total: ${passed + failed}`);
  console.log("=".repeat(70));

  if (failed === 0) {
    console.log("\n🎉 ALL TESTS PASSED!");
    process.exit(0);
  } else {
    console.log("\n❌ SOME TESTS FAILED");
    process.exit(1);
  }
}

runTests();
