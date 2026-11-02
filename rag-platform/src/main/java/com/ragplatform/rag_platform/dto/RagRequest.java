package com.ragplatform.rag_platform.dto;

import lombok.Getter;

@Getter
public class RagRequest {
    

    private String workspace_id;
    private String question;
    private String chatHistory;
    private String compliance_id;

    public String getWorkspace_id() {
        return workspace_id;
    }

    public void setWorkspace_id(String workspace_id) {
        this.workspace_id = workspace_id;
    }

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public String getChatHistory() {
        return chatHistory;
    }

    public void setChatHistory(String chatHistory) {
        this.chatHistory = chatHistory;
    }

    public String getCompliance_id() {
        return compliance_id;
    }

    public void setCompliance_id(String compliance_id) {
        this.compliance_id = compliance_id;
    }






}