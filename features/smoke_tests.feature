Feature: SDLC Pod Smoke Tests
  As a software engineer
  I want to ensure all SDLC tools are accessible
  So that I can perform my development tasks

  Scenario: Verify all front-end URLs are accessible
    Given the SDLC Pod is deployed to Minikube
    Then the VS Code URL should be accessible
    And the SysON URL should be accessible
    And the PenPot URL should be accessible
    And the OpenCode URL should be accessible
    And the Web Terminal URL should be accessible
