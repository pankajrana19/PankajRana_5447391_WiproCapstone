# features/e2e_search_journey.feature
# Best Buy End-to-End Search Journey
#
# Flow: Open → Select US → Login → Search → Add to Cart

Feature: End-to-End Search and Cart Journey
  As a signed-in Best Buy user
  I want to search for a product and add it to my cart
  So that I can purchase it

  @e2e @blocker
  Scenario: E2E — Login, search for laptop, add first available item to cart
    Given I open the Best Buy homepage
    And the homepage is loaded successfully
    When I login with credentials from test_data
    Then I should be logged in or continue as guest
    When I search for the e2e product query
    Then the search results page should load
    And at least 1 result should be present on page 1
    When I add the first available item to cart from the results page
    Then the item should be added to cart successfully
