package com.coldcase.userservice.exception;

public class CaseAlreadyStartedException extends RuntimeException {
    public CaseAlreadyStartedException(String message) {
        super(message);
    }
}
