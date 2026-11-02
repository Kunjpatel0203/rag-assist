package com.ragplatform.rag_platform.controller;

import com.ragplatform.rag_platform.dto.LoginRequest;
import com.ragplatform.rag_platform.dto.ResetPasswordRequest;
import com.ragplatform.rag_platform.model.User;
import com.ragplatform.rag_platform.repository.UserRepository;
import com.ragplatform.rag_platform.security.JwtUtil;
import jakarta.validation.Valid;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;
import com.ragplatform.rag_platform.dto.RegisterRequest;
import com.ragplatform.rag_platform.service.VerificationService;
import com.ragplatform.rag_platform.model.VerificationToken;
import com.ragplatform.rag_platform.repository.VerificationTokenRepository;
import com.ragplatform.rag_platform.service.PasswordResetService;
import com.ragplatform.rag_platform.model.PasswordResetToken;
import com.ragplatform.rag_platform.repository.PasswordResetTokenRepository;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/auth")
public class AuthController {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final VerificationService verificationService;
    private final VerificationTokenRepository tokenRepository;
    private final PasswordResetService passwordResetService;
    private final VerificationTokenRepository verificationTokenRepository;
    private final PasswordResetTokenRepository passwordResetTokenRepository;

    public AuthController(UserRepository userRepository,
                          PasswordEncoder passwordEncoder,
                          JwtUtil jwtUtil, VerificationService verificationService, VerificationTokenRepository tokenRepository, PasswordResetService passwordResetService, VerificationTokenRepository verificationTokenRepository, PasswordResetTokenRepository passwordResetTokenRepository) {

        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
        this.verificationService = verificationService;
        this.tokenRepository = tokenRepository;
        this.passwordResetService = passwordResetService;
        this.verificationTokenRepository = verificationTokenRepository;
        this.passwordResetTokenRepository = passwordResetTokenRepository;
    }

    @PostMapping("/register")
    public User register(@Valid @RequestBody RegisterRequest request) {
        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new RuntimeException("Email already registered");
        }
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw new RuntimeException("Passwords do not match");
        }

        User user = new User();

        user.setFullName(request.getFullName());
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setCompany(request.getCompany());
        user.setRole(request.getRole());

        user.setEmailVerified(false);
        user.setCreatedAt(LocalDateTime.now());

        User savedUser = userRepository.save(user);

        verificationService.createVerificationToken(savedUser);

        return savedUser;
    }

    //@PostMapping("/login") public String login(@RequestBody LoginRequest loginRequest) { Optional<User> userOptional = userRepository.findByEmail(loginRequest.getEmail()); if (userOptional.isEmpty()) { return "User not found"; } User user = userOptional.get(); if (!user.isEmailVerified()) { return "Please verify your email before logging in."; } if (!passwordEncoder.matches( loginRequest.getPassword(), user.getPassword())) { return "Invalid password"; } String token = jwtUtil.generateToken(user.getEmail()); return token; }

    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody LoginRequest loginRequest) {

        Optional<User> userOptional =
                userRepository.findByEmail(loginRequest.getEmail());

        if (userOptional.isEmpty()) {
            return Map.of("error", "User not found");
        }

        User user = userOptional.get();

        if (!user.isEmailVerified()) {
            return Map.of("error", "Please verify your email before logging in.");
        }

        if (!passwordEncoder.matches(
                loginRequest.getPassword(),
                user.getPassword())) {

            return Map.of("error", "Invalid password");
        }

        String token = jwtUtil.generateToken(user.getEmail());

        return Map.of("token", token);
    }

//
@GetMapping("/verify")
public Map<String, String> verifyEmail(@RequestParam String token) {

    VerificationToken verificationToken =
            tokenRepository.findByToken(token)
                    .orElseThrow(() -> new RuntimeException("Invalid token"));

    // ✅ Check token expiry (24 hours)
    if (verificationToken.getCreatedAt().plusHours(24).isBefore(LocalDateTime.now())) {
        return Map.of("error", "Verification link expired. Please request a new verification email.");
    }

    User user = userRepository.findById(verificationToken.getUserId())
            .orElseThrow(() -> new RuntimeException("User not found"));

    user.setEmailVerified(true);
    userRepository.save(user);

    return Map.of("message", "Email verified successfully! You can now login.");
}





//
@PostMapping("/resend-verification")
public Map<String, String> resendVerification(@RequestParam String email) {

    Optional<User> userOptional = userRepository.findByEmail(email);

    if (userOptional.isEmpty()) {
        return Map.of("error", "User not found");
    }

    User user = userOptional.get();

    if (user.isEmailVerified()) {
        return Map.of("error", "Email is already verified.");
    }

    verificationService.createVerificationToken(user);

    return Map.of("message", "Verification email sent successfully.");
}




//    @PostMapping("/forgot-password")
//    public String forgotPassword(@RequestParam String email) {
//
//        Optional<User> userOptional = userRepository.findByEmail(email);
//
//        if (userOptional.isEmpty()) {
//            return "User not found";
//        }
//
//        User user = userOptional.get();
//
//        passwordResetService.createPasswordResetToken(user);
//
//        return "Password reset email sent successfully.";
//    }

    @PostMapping("/forgot-password")
    public Map<String, String> forgotPassword(@RequestParam String email) {

        Optional<User> userOptional = userRepository.findByEmail(email);

        if (userOptional.isEmpty()) {
            return Map.of("error", "User not found");
        }

        User user = userOptional.get();

        passwordResetService.createPasswordResetToken(user);

        return Map.of("message", "Password reset email sent successfully.");
    }




//    @PostMapping("/reset-password")
//    public String resetPassword(@RequestBody ResetPasswordRequest request) {
//
//        Optional<PasswordResetToken> tokenOptional =
//                passwordResetTokenRepository.findByToken(request.getToken());
//
//        if (tokenOptional.isEmpty()) {
//            return "Invalid or expired token";
//        }
//
//        PasswordResetToken resetToken = tokenOptional.get();
//
//        Optional<User> userOptional =
//                userRepository.findById(resetToken.getUserId());
//
//        if (userOptional.isEmpty()) {
//            return "User not found";
//        }
//
//        User user = userOptional.get();
//
//        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
//
//        userRepository.save(user);
//
//        passwordResetTokenRepository.delete(resetToken);
//
//        return "Password reset successfully";
//    }

    @PostMapping("/reset-password")
    public Map<String, String> resetPassword(@RequestBody ResetPasswordRequest request) {

        Optional<PasswordResetToken> tokenOptional =
                passwordResetTokenRepository.findByToken(request.getToken());

        if (tokenOptional.isEmpty()) {
            return Map.of("error", "Invalid or expired token");
        }

        PasswordResetToken resetToken = tokenOptional.get();

        Optional<User> userOptional =
                userRepository.findById(resetToken.getUserId());

        if (userOptional.isEmpty()) {
            return Map.of("error", "User not found");
        }

        User user = userOptional.get();

        user.setPassword(passwordEncoder.encode(request.getNewPassword()));

        userRepository.save(user);

        passwordResetTokenRepository.delete(resetToken);

        return Map.of("message", "Password reset successfully");
    }
}