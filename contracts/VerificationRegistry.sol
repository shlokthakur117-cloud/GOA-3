// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract VerificationRegistry {
    
    struct VerificationRecord {
        bytes32 fingerprint;
        string source;
        uint256 timestamp;
        address submitter;
    }

    // Mapping from fingerprint to VerificationRecord
    mapping(bytes32 => VerificationRecord) public records;

    event VerificationStored(
        bytes32 indexed fingerprint,
        string source,
        uint256 timestamp,
        address submitter
    );

    /**
     * @dev Stores a new verification record. 
     *      Will revert if a record with the same fingerprint already exists.
     */
    function storeVerification(
        bytes32 _fingerprint,
        string memory _source,
        uint256 _timestamp
    ) public {
        require(records[_fingerprint].timestamp == 0, "Record already exists");

        records[_fingerprint] = VerificationRecord({
            fingerprint: _fingerprint,
            source: _source,
            timestamp: _timestamp,
            submitter: msg.sender
        });

        emit VerificationStored(_fingerprint, _source, _timestamp, msg.sender);
    }

    /**
     * @dev Retrieves a verification record by its fingerprint.
     */
    function getVerification(bytes32 _fingerprint) public view returns (
        bytes32 fingerprint,
        string memory source,
        uint256 timestamp,
        address submitter
    ) {
        VerificationRecord memory record = records[_fingerprint];
        require(record.timestamp != 0, "Record not found");

        return (
            record.fingerprint,
            record.source,
            record.timestamp,
            record.submitter
        );
    }
}
