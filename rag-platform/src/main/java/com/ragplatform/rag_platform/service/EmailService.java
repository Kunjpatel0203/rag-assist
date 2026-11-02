package com.ragplatform.rag_platform.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    @Autowired
    private JavaMailSender mailSender;

    public void sendVerificationEmail(String toEmail, String verificationLink) {

        SimpleMailMessage message = new SimpleMailMessage();

        message.setTo(toEmail);
        message.setSubject("Verify your email - RAG Platform");

        message.setText(
                "Welcome to RAG Platform!\n\n" +
                        "Please verify your email by clicking the link below:\n\n" +
                        verificationLink +
                        "\n\nIf you did not create this account, ignore this email."
        );

        mailSender.send(message);
    }
}