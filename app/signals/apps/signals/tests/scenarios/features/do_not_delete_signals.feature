# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2023 Gemeente Amsterdam
Feature: Do not delete Signals
  Scenario Outline: Do not delete a Signal in the state Completed for x years
    Given a Signal exists in the state Completed and the state has been set <years> years ago
    When the system runs the task to delete Signals in Completed for more than 5 years
    Then the Signal should not have been deleted

    Examples:
    | years  |
    |  0     |
    |  1     |
    |  2     |

  Scenario Outline: Do not delete a Signal in the state Cancelled for x years
    Given a Signal exists in the state Cancelled and the state has been set <years> years ago
    When the system runs the task to delete Signals in Cancelled for more than 5 years
    Then the Signal should not have been deleted

    Examples:
    | years  |
    |  1     |
    |  2     |
    |  3     |

  Scenario Outline: Do not delete a Signal in the state Split for x years
    Given a Signal exists in the state Split and the state has been set <years> years ago
    When the system runs the task to delete Signals in Split for more than 5 years
    Then the Signal should not have been deleted

    Examples:
    | years  |
    |  2     |
    |  3     |
    |  4     |
