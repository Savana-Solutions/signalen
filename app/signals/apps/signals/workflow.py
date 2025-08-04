# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2018 - 2022 Gemeente Amsterdam, Vereniging van Nederlandse Gemeenten
"""
Model the workflow of responding to a Signal (melding) as state machine.
"""
# Note on historical states: to leave the historical data intact, old states are
# retained below (but made unreachable if at all possible).

# Internal statusses
LEEG = ''
REPORTED = 'm'
AWAITING = 'i'
IN_PROGRESS = 'b'
ON_HOLD = 'h'
COMPLETED = 'o'
CANCELLED = 'a'
SPLIT = 's'  # Historical state - new `signal.Signal` instances will not get this state ever.
REOPENED = 'reopened'
CLOSURE_REQUESTED = 'closure requested'
PLANNED = 'planned'
REQUEST_TO_REOPEN = 'reopen requested'
REACTION_REQUESTED = 'reaction requested'
REACTION_RECEIVED = 'reaction received'
FORWARDED_TO_EXTERN = 'forward to external'

# Statusses to track progress in external systems
TO_SEND = 'ready to send'
SENT = 'sent'
SEND_FAILED = 'send failed'
DONE_EXTERNAL = 'done external'

# Choices for the API/Serializer layer. Users that can change the state via the API are only allowed
# to use one of the following choices.
STATUS_CHOICES_API = (
    (REPORTED, 'Reported'),
    (AWAITING, 'Awaiting handling'),
    (IN_PROGRESS, 'In progress'),
    (ON_HOLD, 'On hold'),
    (PLANNED, 'Planned'),
    (TO_SEND, 'External: to send'),
    (COMPLETED, 'Completed'),
    (CANCELLED, 'Cancelled'),
    (REOPENED, 'Reopened'),
    (SPLIT, 'Split'),
    (CLOSURE_REQUESTED, 'External: closure requested'),
    (REACTION_REQUESTED, 'Reaction requested'),
    (REACTION_RECEIVED, 'Reaction received'),
    (FORWARDED_TO_EXTERN, 'Forwarded to extern'),
)

# Choices used by the application. These choices can be set from within the application, not via the
# API/Serializer layer.
STATUS_CHOICES_APP = (
    (SENT, 'External: sent'),
    (SEND_FAILED, 'External: failed'),
    (DONE_EXTERNAL, 'External: completed'),
    (REQUEST_TO_REOPEN, 'Request to reopen'),
)

# All allowed choices, used for the model `Status`.
STATUS_CHOICES = STATUS_CHOICES_API + STATUS_CHOICES_APP

ALLOWED_STATUS_CHANGES = {
    LEEG: [
        REPORTED
    ],
    REPORTED: [
        REPORTED,  # SIG-1264
        AWAITING,
        IN_PROGRESS,
        TO_SEND,
        COMPLETED,  # SIG-1294
        CANCELLED,  # Op verzoek via mail van Arvid Smits
        PLANNED,  # SIG-1327
        REACTION_REQUESTED,  # SIG-3651
        FORWARDED_TO_EXTERN,  # PS-261
    ],
    AWAITING: [
        REPORTED,  # SIG-1264
        AWAITING,
        PLANNED,
        CLOSURE_REQUESTED,
        COMPLETED,
        TO_SEND,  # SIG-1293
        IN_PROGRESS,  # SIG-1295
        CANCELLED,  # SIG-2987
        REACTION_REQUESTED,  # SIG-3651
        FORWARDED_TO_EXTERN,  # PS-261
    ],
    IN_PROGRESS: [
        REPORTED,  # SIG-1264
        PLANNED,
        IN_PROGRESS,
        COMPLETED,
        CANCELLED,
        TO_SEND,
        CLOSURE_REQUESTED,  # SIG-1374
        REACTION_REQUESTED,  # SIG-3651
        FORWARDED_TO_EXTERN,  # PS-261
    ],
    PLANNED: [
        REPORTED,  # SIG-1264
        PLANNED,
        IN_PROGRESS,
        COMPLETED,
        CANCELLED,
        CLOSURE_REQUESTED,  # SIG-1293
        REACTION_REQUESTED,  # SIG-3651
        FORWARDED_TO_EXTERN,  # PS-261
    ],
    ON_HOLD: [
        PLANNED,
        CANCELLED,  # SIG-2987
    ],
    TO_SEND: [
        SENT,
        SEND_FAILED,
        CANCELLED,  # SIG-2987
    ],
    SENT: [
        DONE_EXTERNAL,
        CANCELLED,  # SIG-2987
    ],
    SEND_FAILED: [
        REPORTED,
        TO_SEND,
        CANCELLED,  # SIG-2987
    ],
    DONE_EXTERNAL: [
        COMPLETED,
        CANCELLED,
        IN_PROGRESS,  # SIG-1293
    ],
    COMPLETED: [
        REOPENED,
        REQUEST_TO_REOPEN,
    ],
    CANCELLED: [
        CANCELLED,
        REOPENED,
        IN_PROGRESS,  # SIG-2109
    ],
    REOPENED: [
        REOPENED,
        IN_PROGRESS,
        COMPLETED,
        CANCELLED,
        TO_SEND,
        REPORTED,  # SIG-1374
        REACTION_REQUESTED,  # SIG-3948
        FORWARDED_TO_EXTERN,  # PS-261
    ],
    SPLIT: [],
    CLOSURE_REQUESTED: [
        REPORTED,  # SIG-1264
        CLOSURE_REQUESTED,
        AWAITING,
        COMPLETED,
        CANCELLED,
        IN_PROGRESS,  # SIG-1374
        FORWARDED_TO_EXTERN,  # PS-261
    ],
    REQUEST_TO_REOPEN: [
        COMPLETED,
        REOPENED,
        CANCELLED,
    ],
    REACTION_REQUESTED: [  # SIG-3651
        REPORTED,
        AWAITING,
        IN_PROGRESS,
        PLANNED,
        COMPLETED,
        CANCELLED,
        REACTION_REQUESTED,
        REACTION_RECEIVED,
        TO_SEND,
        FORWARDED_TO_EXTERN,  # PS-261
    ],
    REACTION_RECEIVED: [  # SIG-3651
        REPORTED,
        AWAITING,
        IN_PROGRESS,
        COMPLETED,
        CANCELLED,
        PLANNED,
        REACTION_REQUESTED,
        TO_SEND,
        FORWARDED_TO_EXTERN,  # PS-261
    ],
    FORWARDED_TO_EXTERN: [
        CLOSURE_REQUESTED,
        REPORTED,
        AWAITING,
        IN_PROGRESS,
        FORWARDED_TO_EXTERN,
        PLANNED,
        COMPLETED,
        CANCELLED,
        REACTION_REQUESTED,
        REACTION_RECEIVED,
        TO_SEND,
    ]
}
