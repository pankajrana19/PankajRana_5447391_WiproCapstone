# features/search.feature
# Best Buy Search Bar — Positive and Negative Test Cases
#
# All test data is loaded from config/test_data.json

Feature: Best Buy Search Bar
  As a user of Best Buy
  I want to use the search bar to find products
  So that I can browse and purchase items I need

  Background:
    Given I open the Best Buy homepage
    And the homepage is loaded successfully

  # ── Positive Test Cases ─────────────────────────────────────── #

  @positive @critical
  Scenario: TC_POS_01 — Valid product search returns results
    Given I am on the Best Buy homepage
    When I search for the "basic_search" product query
    Then the URL should indicate a search results page
    And at least 1 product result should be visible

  @positive @normal
  Scenario: TC_POS_02 — Search result titles match the query keyword
    Given I am on the Best Buy homepage
    When I search for the "title_match" product query
    Then the results page should load successfully
    And at least 30 percent of result titles should contain a relevant keyword

  @positive @minor
  Scenario: TC_POS_03 — Search bar retains the typed query after search
    Given I am on the Best Buy homepage
    When I search for the "search_bar_retain" product query
    Then the search bar should still display the typed query

  @positive @normal
  Scenario: TC_POS_04 — Gibberish query is handled gracefully
    Given I am on the Best Buy homepage
    When I search for the "gibberish" product query
    Then the site should not show a server error
    And the site should either show results or a no-results message

  # ── Negative Test Cases ─────────────────────────────────────── #

  @negative @critical
  Scenario: TC_NEG_01 — Invalid login credentials show error message
    Given I navigate to the Best Buy login page
    When I enter invalid login credentials
    Then the login should be rejected
    And an error message should be shown or the user should remain on the login page

  @negative @minor
  Scenario: TC_NEG_02 — Special characters search is handled gracefully
    Given I am on the Best Buy homepage
    When I search for the "special_characters" negative query
    Then the site should not show a server error
    And the search should return zero results or a no-results message
