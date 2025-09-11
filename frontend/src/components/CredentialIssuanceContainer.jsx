import React, { useState } from 'react';
import { motion } from 'framer-motion';
// import { Button } from "./ui/button";
// import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./ui/card";
// import { Label } from "./ui/label";
// import { Input } from "./ui/input";
// import { Textarea } from "./ui/textarea";
// import { useToast } from "./ui/use-toast";
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

const CredentialIssuanceContainer = () => {
  const { toast } = useToast();
  const [form, setForm] = useState({
    studentId: '',
    credentialType: '',
    details: '',
    expiryDate: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (value, name) => {
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Example API call, replace with your actual API
      // await api.post('/credentials/issue', form);
      
      toast({
        title: "Credential Issued",
        description: "The credential has been successfully issued to the student.",
        variant: "success",
      });
      
      // Reset form
      setForm({
        studentId: '',
        credentialType: '',
        details: '',
        expiryDate: ''
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to issue credential. Please try again.",
        variant: "destructive",
      });
      console.error("Issue credential error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto p-4"
    >
      <Card>
        <CardHeader>
          <CardTitle>Issue New Credential</CardTitle>
          <CardDescription>
            Fill in the details to issue a new verifiable credential to a student
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="studentId">Student ID</Label>
                <Input
                  id="studentId"
                  name="studentId"
                  placeholder="Enter student ID"
                  value={form.studentId}
                  onChange={handleChange}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="credentialType">Credential Type</Label>
                <Select
                  value={form.credentialType}
                  onValueChange={(value) => handleSelectChange(value, 'credentialType')}
                  required
                >
                  <SelectTrigger id="credentialType">
                    <SelectValue placeholder="Select credential type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="degree">Degree</SelectItem>
                    <SelectItem value="certificate">Certificate</SelectItem>
                    <SelectItem value="transcript">Transcript</SelectItem>
                    <SelectItem value="diploma">Diploma</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="details">Credential Details</Label>
              <Textarea
                id="details"
                name="details"
                placeholder="Enter detailed information about this credential"
                value={form.details}
                onChange={handleChange}
                rows={5}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="expiryDate">Expiry Date (optional)</Label>
              <Input
                id="expiryDate"
                name="expiryDate"
                type="date"
                value={form.expiryDate}
                onChange={handleChange}
              />
            </div>
          </form>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => setForm({
            studentId: '',
            credentialType: '',
            details: '',
            expiryDate: ''
          })}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Issuing..." : "Issue Credential"}
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
};

export default CredentialIssuanceContainer;
